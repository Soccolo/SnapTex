from __future__ import annotations

import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageGrab, ImageTk

from .capture import ScreenSelector
from .core import Pix2TexRecognizer, Recognizer


BG = "#07111f"
PANEL = "#0d1b2d"
TEXT = "#edf7ff"
MUTED = "#96a8bd"
ACCENT = "#5eead4"


class SnapTexApp:
    def __init__(self, root: tk.Tk, recognizer: Recognizer | None = None) -> None:
        self.root = root
        self.recognizer = recognizer or Pix2TexRecognizer()
        self.image: Image.Image | None = None
        self.preview: ImageTk.PhotoImage | None = None
        self.results: queue.Queue[tuple[str, str]] = queue.Queue()

        root.title("SnapTeX")
        root.geometry("760x620")
        root.minsize(620, 520)
        root.configure(bg=BG)
        self._configure_styles()
        self._build_ui()
        self.root.after(100, self._poll_results)

    def _configure_styles(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 28, "bold"))
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure(
            "Accent.TButton",
            background=ACCENT,
            foreground="#05201d",
            padding=(18, 11),
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
        )
        style.map("Accent.TButton", background=[("active", "#99f6e4")])
        style.configure(
            "Quiet.TButton",
            background="#17283e",
            foreground=TEXT,
            padding=(16, 10),
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.map("Quiet.TButton", background=[("active", "#233a57")])

    def _build_ui(self) -> None:
        shell = ttk.Frame(self.root, padding=28)
        shell.pack(fill="both", expand=True)

        ttk.Label(shell, text="SnapTeX", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            shell,
            text="Turn any equation on your screen into LaTeX — locally.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(2, 20))

        actions = ttk.Frame(shell)
        actions.pack(fill="x", pady=(0, 18))
        self.capture_button = ttk.Button(
            actions,
            text="Capture equation",
            style="Accent.TButton",
            command=self.capture,
        )
        self.capture_button.pack(side="left")
        ttk.Button(
            actions,
            text="Use clipboard image",
            style="Quiet.TButton",
            command=self.from_clipboard,
        ).pack(side="left", padx=10)

        preview_panel = ttk.Frame(shell, style="Panel.TFrame", padding=16)
        preview_panel.pack(fill="both", expand=True)
        self.preview_label = tk.Label(
            preview_panel,
            text="Your equation screenshot will appear here",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 11),
        )
        self.preview_label.pack(fill="both", expand=True)

        ttk.Label(shell, text="LaTeX", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", pady=(18, 6)
        )
        output_row = ttk.Frame(shell)
        output_row.pack(fill="x")
        self.output = tk.Text(
            output_row,
            height=4,
            wrap="word",
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            padx=14,
            pady=12,
            font=("Cascadia Mono", 11),
        )
        self.output.pack(side="left", fill="both", expand=True)
        self.copy_button = ttk.Button(
            output_row,
            text="Copy",
            style="Quiet.TButton",
            command=self.copy_latex,
            state="disabled",
        )
        self.copy_button.pack(side="left", padx=(10, 0), fill="y")

        self.status = tk.StringVar(value="Ready")
        ttk.Label(shell, textvariable=self.status, style="Muted.TLabel").pack(
            anchor="w", pady=(10, 0)
        )

    def capture(self) -> None:
        self.root.withdraw()
        self.root.after(
            150,
            lambda: ScreenSelector(self.root, self._capture_complete, self._capture_cancelled),
        )

    def _capture_complete(self, image: Image.Image) -> None:
        self.root.deiconify()
        self.root.lift()
        self._set_image(image)
        self._recognize()

    def _capture_cancelled(self) -> None:
        self.root.deiconify()
        self.status.set("Capture cancelled")

    def from_clipboard(self) -> None:
        value = ImageGrab.grabclipboard()
        if isinstance(value, Image.Image):
            self._set_image(value)
            self._recognize()
            return
        messagebox.showinfo("No image found", "Copy an image first, then try again.")

    def _set_image(self, image: Image.Image) -> None:
        self.image = image.copy()
        display = image.copy()
        display.thumbnail((660, 270))
        self.preview = ImageTk.PhotoImage(display)
        self.preview_label.configure(image=self.preview, text="")

    def _recognize(self) -> None:
        if self.image is None:
            return
        self.capture_button.configure(state="disabled")
        self.copy_button.configure(state="disabled")
        self.output.delete("1.0", "end")
        self.status.set("Reading equation… first use may download the model")
        image = self.image.copy()

        def worker() -> None:
            try:
                latex = self.recognizer.recognize(image)
                self.results.put(("ok", latex))
            except Exception as exc:  # surfaced in the UI, not lost in a worker thread
                self.results.put(("error", str(exc)))

        threading.Thread(target=worker, daemon=True).start()

    def _poll_results(self) -> None:
        try:
            kind, value = self.results.get_nowait()
        except queue.Empty:
            self.root.after(100, self._poll_results)
            return

        self.capture_button.configure(state="normal")
        if kind == "ok":
            self.output.insert("1.0", value)
            self.copy_button.configure(state="normal")
            self.status.set("Done — review the result, then copy it")
        else:
            self.status.set("Recognition failed")
            messagebox.showerror(
                "Could not read the equation",
                f"{value}\n\nTry a tighter, higher-contrast crop.",
            )
        self.root.after(100, self._poll_results)

    def copy_latex(self) -> None:
        latex = self.output.get("1.0", "end-1c").strip()
        if not latex:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(latex)
        self.status.set("Copied LaTeX to clipboard")


def main() -> None:
    root = tk.Tk()
    SnapTexApp(root)
    root.mainloop()
