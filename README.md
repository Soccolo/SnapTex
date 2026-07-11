# SnapTeX

SnapTeX is a small Windows desktop app that turns a screenshot of a mathematical equation into LaTeX. Recognition runs locally with [pix2tex](https://github.com/lukas-blecher/LaTeX-OCR), so there is no subscription or per-image API charge.

## What it does

- Drag over an equation anywhere on your screen
- Read an equation image copied to the clipboard
- Preview the captured image
- Copy clean LaTeX with one click
- Keep the AI model local after its first download

## Quick start (Windows)

1. Install Python 3.10 or 3.11 from [python.org](https://www.python.org/downloads/windows/) and enable **Add Python to PATH**.
2. Double-click `setup.bat`.
3. Double-click `run.bat`.
4. Click **Capture equation**, drag a box around an equation, and release.

The first recognition can take a minute because pix2tex downloads its model. Later runs use the cached model. CPU recognition works, though a supported GPU is faster.

## Build a standalone app

After running `setup.bat`, open PowerShell in this folder and run:

```powershell
.\build.ps1
```

The packaged app will be placed in `dist\SnapTeX\`. The model is downloaded to the user's cache on first use rather than being bundled into the executable.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest
python -m snaptex
```

## Privacy

Screenshots stay on your laptop. The app does not upload images or include analytics. On first use, pix2tex may connect to the internet to download its model files.

## Known limitations

- Best results come from tightly cropped, high-contrast equations.
- Handwriting and multi-line derivations can be less accurate than printed equations.
- The screen selector uses one overlay per monitor; on unusual mixed-DPI setups, clipboard input is a reliable fallback.

## License

MIT. The pix2tex model and dependencies have their own licenses.
