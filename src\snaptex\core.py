from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

from PIL import Image


class Recognizer(Protocol):
    def recognize(self, image: Image.Image) -> str: ...


class Pix2TexRecognizer:
    """Lazily loads pix2tex so the window appears immediately."""

    def __init__(self) -> None:
        self._model = None

    def recognize(self, image: Image.Image) -> str:
        if self._model is None:
            from pix2tex.cli import LatexOCR

            self._model = LatexOCR()
        return normalize_latex(self._model(image.convert("RGB")))


def normalize_latex(value: str) -> str:
    """Remove wrappers commonly returned by OCR while preserving the equation."""
    result = value.strip()
    wrappers = (
        ("$$", "$$"),
        ("\\[", "\\]"),
        ("\\(", "\\)"),
        ("$", "$"),
    )
    for start, end in wrappers:
        if result.startswith(start) and result.endswith(end):
            result = result[len(start) : -len(end)].strip()
            break
    return re.sub(r"[ \t]+", " ", result)


@dataclass(frozen=True)
class DragBox:
    start_x: int
    start_y: int
    end_x: int
    end_y: int

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        return (
            min(self.start_x, self.end_x),
            min(self.start_y, self.end_y),
            max(self.start_x, self.end_x),
            max(self.start_y, self.end_y),
        )

    @property
    def is_large_enough(self) -> bool:
        left, top, right, bottom = self.bounds
        return right - left >= 8 and bottom - top >= 8
