from __future__ import annotations

import ctypes
import tkinter as tk
from collections.abc import Callable

from PIL import Image, ImageGrab

from .core import DragBox


def _virtual_screen() -> tuple[int, int, int, int]:
    """Return the complete Windows desktop bounds, including negative origins."""
    user32 = ctypes.windll.user32
    left = user32.GetSystemMetrics(76)
    top = user32.GetSystemMetrics(77)
    width = user32.GetSystemMetrics(78)
    height = user32.GetSystemMetrics(79)
    return left, top, width, height


class ScreenSelector:
    def __init__(
        self,
        parent: tk.Tk,
        on_capture: Callable[[Image.Image], None],
        on_cancel: Callable[[], None],
    ) -> None:
        self.parent = parent
        self.on_capture = on_capture
        self.on_cancel = on_cancel
        self.start: tuple[int, int] | None = None
        self.rectangle: int | None = None

        left, top, width, height = _virtual_screen()
        self.origin = (left, top)
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.28)
        self.window.configure(bg="#07111f")
        self.window.geometry(f"{width}x{height}{left:+d}{top:+d}")

        self.canvas = tk.Canvas(
            self.window, bg="#07111f", cursor="crosshair", highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_text(
            width // 2,
            40,
            text="Drag around an equation  •  Esc to cancel",
            fill="white",
            font=("Segoe UI", 16, "bold"),
        )
        self.canvas.bind("<ButtonPress-1>", self._press)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._release)
        self.window.bind("<Escape>", lambda _event: self._cancel())
        self.window.focus_force()

    def _press(self, event: tk.Event) -> None:
        self.start = (event.x, event.y)
        self.rectangle = self.canvas.create_rectangle(
            event.x,
            event.y,
            event.x,
            event.y,
            outline="#5eead4",
            width=3,
            fill="#ffffff",
        )

    def _drag(self, event: tk.Event) -> None:
        if self.start and self.rectangle:
            self.canvas.coords(self.rectangle, *self.start, event.x, event.y)

    def _release(self, event: tk.Event) -> None:
        if not self.start:
            return
        box = DragBox(*self.start, event.x, event.y)
        if not box.is_large_enough:
            self._cancel()
            return

        left, top, right, bottom = box.bounds
        origin_x, origin_y = self.origin
        absolute_bounds = (
            left + origin_x,
            top + origin_y,
            right + origin_x,
            bottom + origin_y,
        )
        self.window.withdraw()
        self.window.update_idletasks()
        try:
            image = ImageGrab.grab(bbox=absolute_bounds, all_screens=True)
        except Exception:
            self.window.destroy()
            self.on_cancel()
            raise
        self.window.destroy()
        self.on_capture(image)

    def _cancel(self) -> None:
        self.window.destroy()
        self.on_cancel()
