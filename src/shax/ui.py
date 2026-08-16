from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from .config import save_config

# Centralized modern palette
PRIMARY = "#2563EB"
PRIMARY_HOVER = "#1D4ED8"
ACCENT = "#059669"
ACCENT_HOVER = "#047857"
DARK = "#0B1020"
PANEL = "#0B1223"
SURFACE = "#111827"
MUTED = "#9CA3AF"
TEXT = "#E2E8F0"
STATUS_READY = "#34D399"
STATUS_ACTIVE = "#FBBF24"
STATUS_ERROR = "#F87171"


def _add_hover(widget: tk.Widget, enter_bg: str, leave_bg: str) -> None:
    """Simple hover helper for tk widgets (best-effort, no side effects).

    Keeps behavior conservative to avoid platform-specific issues.
    """
    try:
        widget.bind("<Enter>", lambda e: widget.config(bg=enter_bg))
        widget.bind("<Leave>", lambda e: widget.config(bg=leave_bg))
    except Exception:
        # Fail silently — hover effects are cosmetic
        pass


class TinyWindow:
    def __init__(self, app: object, title: str = "Jerbud") -> None:
        self.app = app
        self.root = tk.Tk()
        self.root.title(title)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#0B1020")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 320
        height = 150
        x = (screen_width // 2) - (width // 2)
        y = screen_height - height - 28
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        outer = tk.Frame(self.root, bg="#0B1020", padx=14, pady=12)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg="#0B1020")
        header.pack(fill="x")

        brand = tk.Label(
            header,
            text=title,
            fg="#E2E8F0",
            bg="#0B1020",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        brand.pack(side="left")

        self.exit_button = tk.Button(
            header,
            text="×",
            width=2,
            bg=SURFACE,
            fg=TEXT,
            activebackground="#1F2937",
            activeforeground="#F8FAFC",
            bd=0,
            padx=6,
            pady=4,
            command=self.exit_app,
            relief="flat",
            highlightthickness=0,
            font=("Segoe UI", 12, "bold"),
            cursor="hand2",
        )
        self.exit_button.pack(side="right")
        _add_hover(self.exit_button, "#2B2F36", SURFACE)

        # Allow dragging the window by its header (overrideredirect windows need custom drag)
        def _start_move(event):
            # record the starting positions for root and pointer
            self._drag_start_x = event.x_root
            self._drag_start_y = event.y_root
            self._win_start_x = self.root.winfo_x()
            self._win_start_y = self.root.winfo_y()

        def _do_move(event):
            dx = event.x_root - getattr(self, "_drag_start_x", event.x_root)
            dy = event.y_root - getattr(self, "_drag_start_y", event.y_root)
            try:
                new_x = self._win_start_x + dx
                new_y = self._win_start_y + dy
                self.root.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}+{new_x}+{new_y}")
            except Exception:
                pass

        header.bind("<ButtonPress-1>", _start_move)
        header.bind("<B1-Motion>", _do_move)
        brand.bind("<ButtonPress-1>", _start_move)
        brand.bind("<B1-Motion>", _do_move)

        self.status_var = tk.StringVar(value="Ready")
        status_row = tk.Frame(outer, bg="#0B1020")
        status_row.pack(fill="x", pady=(12, 10))

        self.status_dot = tk.Label(
            status_row,
            text="●",
            fg="#34D399",
            bg="#0B1020",
            font=("Segoe UI", 10),
        )
        self.status_dot.pack(side="left", padx=(0, 6))

        self.status_label = tk.Label(
            status_row,
            textvariable=self.status_var,
            fg="#E2E8F0",
            bg="#0B1020",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        controls = tk.Frame(outer, bg="#0B1020")
        controls.pack(fill="x")

        self.toggle_button = tk.Button(
            controls,
            text="Listen",
            width=14,
            bg=PRIMARY,
            fg="white",
            activebackground=PRIMARY_HOVER,
            activeforeground="white",
            bd=0,
            padx=12,
            pady=9,
            command=self.app.toggle_recording,
            relief="flat",
            highlightthickness=0,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.toggle_button.pack(side="left", expand=True, fill="x")
        _add_hover(self.toggle_button, PRIMARY_HOVER, PRIMARY)

        self.settings_button = tk.Button(
            controls,
            text="Settings",
            width=12,
            bg=SURFACE,
            fg=TEXT,
            activebackground="#1F2937",
            activeforeground="white",
            bd=0,
            padx=12,
            pady=9,
            command=self.show_settings,
            relief="flat",
            highlightthickness=0,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        self.settings_button.pack(side="left", padx=(10, 0), expand=True, fill="x")
        _add_hover(self.settings_button, "#1F2937", SURFACE)

        self.root.bind("<Escape>", lambda *_: self.exit_app())

    def show_settings(self) -> None:
        # Create a non-modal settings dialog so users can edit options
        cfg = self.app.config
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.transient(self.root)
        win.grab_set()
        win.geometry("420x320")
        win.configure(bg="#0B1020")

        frame = tk.Frame(win, bg="#0B1020", padx=14, pady=12)
        frame.pack(fill="both", expand=True)

        # Hotkey
        tk.Label(frame, text="Start/Stop hotkey:", fg="#E2E8F0", bg="#0B1020").pack(anchor="w")
        hotkey_var = tk.StringVar(value=cfg.hotkey)
        hotkey_entry = tk.Entry(frame, textvariable=hotkey_var, bg="#0B1223", fg="#E2E8F0", insertbackground="#E2E8F0")
        hotkey_entry.pack(fill="x", pady=(0, 8))
        tk.Label(frame, text="Use format: ctrl+alt+shift+s (order: modifiers + key)", fg="#9CA3AF", bg="#0B1020").pack(anchor="w")

        # Language
        tk.Label(frame, text="Language (ISO code):", fg="#E2E8F0", bg="#0B1020").pack(anchor="w", pady=(8, 0))
        lang_var = tk.StringVar(value=cfg.language)
        lang_entry = tk.Entry(frame, textvariable=lang_var, bg="#0B1223", fg="#E2E8F0", insertbackground="#E2E8F0")
        lang_entry.pack(fill="x")

        # Auto-paste
        auto_paste_var = tk.BooleanVar(value=cfg.auto_paste)
        tk.Checkbutton(frame, text="Auto-paste transcript", variable=auto_paste_var, fg="#E2E8F0", bg="#0B1020", selectcolor="#0B1020", activebackground="#0B1020").pack(anchor="w", pady=(8, 0))

        # Automatic corrections: fillers and grammar
        tk.Label(frame, text="Automatic post-processing:", fg="#E2E8F0", bg="#0B1020").pack(anchor="w", pady=(12, 0))
        fix_fillers_var = tk.BooleanVar(value=getattr(cfg, "auto_fix_fillers", False))
        grammar_var = tk.BooleanVar(value=getattr(cfg, "auto_grammar", False))
        tk.Checkbutton(frame, text="Remove common filler words (uh, umm, like)", variable=fix_fillers_var, fg="#E2E8F0", bg="#0B1020", selectcolor="#0B1020", activebackground="#0B1020").pack(anchor="w")
        tk.Checkbutton(frame, text="Light grammar correction", variable=grammar_var, fg="#E2E8F0", bg="#0B1020", selectcolor="#0B1020", activebackground="#0B1020").pack(anchor="w")

        # Help / recommendation text (compact) + more button
        help_frame = tk.Frame(frame, bg="#0B1020")
        help_frame.pack(fill="x", pady=(10, 0))
        tk.Label(help_frame, text="Recommendation:", fg=TEXT, bg=DARK).pack(anchor="w")
        tk.Label(help_frame, text="Use rule-based filler removal first, then a light grammar pass (local or privacy-respecting model).",
                 fg=MUTED, bg=DARK).pack(anchor="w")
 
        def show_recommendation() -> None:
            messagebox.showinfo(
                "Auto-corrections recommendation",
                (
                    "Recommended approach:\n\n"
                    "1) Run a small, deterministic pass to remove common filler words (e.g. 'uh', 'umm', 'like').\n"
                    "   This is fast, deterministic, and preserves user privacy.\n\n"
                    "2) Optionally run a light grammar-correction pass: use a local small model or an on-device rule-based tool (e.g. language-tool-python)",
                ),
            )
 
        more_btn = tk.Button(frame, text="More...", command=show_recommendation, bg=SURFACE, fg=TEXT, bd=0, cursor="hand2")
        more_btn.pack(anchor="e", pady=(6, 0))
        _add_hover(more_btn, "#1F2937", SURFACE)

        # Buttons
        btn_frame = tk.Frame(frame, bg="#0B1020")
        btn_frame.pack(fill="x", pady=(14, 0))

        def restore_defaults() -> None:
            hotkey_var.set("ctrl+shift+alt+s")
            lang_var.set("en")
            auto_paste_var.set(True)
            fix_fillers_var.set(False)
            grammar_var.set(False)

        def apply_changes(save: bool = False) -> None:
            # Update in-memory config
            cfg.hotkey = hotkey_var.get().strip() or cfg.hotkey
            cfg.language = lang_var.get().strip() or cfg.language
            cfg.auto_paste = bool(auto_paste_var.get())
            setattr(cfg, "auto_fix_fillers", bool(fix_fillers_var.get()))
            setattr(cfg, "auto_grammar", bool(grammar_var.get()))

            # Persist if requested
            try:
                save_config(cfg)
            except Exception as exc:  # pragma: no cover - I/O
                messagebox.showwarning("Save failed", f"Failed to save settings: {exc}")

            # Tell application to apply changes immediately
            try:
                self.app.apply_config()
            except Exception:
                # Don't crash UI if apply fails; show notice
                messagebox.showinfo("Applied", "Settings updated — restart app if changes are not active.")

            if save:
                win.destroy()

        restore_btn = tk.Button(btn_frame, text="Restore defaults", command=restore_defaults, bg=SURFACE, fg=TEXT, bd=0, cursor="hand2")
        restore_btn.pack(side="left")
        _add_hover(restore_btn, "#1A1C20", SURFACE)

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=win.destroy, bg=SURFACE, fg=TEXT, bd=0, cursor="hand2")
        cancel_btn.pack(side="right")
        _add_hover(cancel_btn, "#1A1C20", SURFACE)

        apply_btn = tk.Button(btn_frame, text="Apply", command=lambda: apply_changes(save=False), bg=PRIMARY, fg="white", bd=0, cursor="hand2")
        apply_btn.pack(side="right", padx=(0, 6))
        _add_hover(apply_btn, PRIMARY_HOVER, PRIMARY)

        save_btn = tk.Button(btn_frame, text="Save & Close", command=lambda: apply_changes(save=True), bg=ACCENT, fg="white", bd=0, cursor="hand2")
        save_btn.pack(side="right", padx=(0, 6))
        _add_hover(save_btn, ACCENT_HOVER, ACCENT)

        win.wait_window()

    def exit_app(self) -> None:
        self.app.stop()

    def set_status(self, text: str) -> None:
        self.status_var.set(text)
        if text.lower().startswith("listening") or text.lower().startswith("transcribing"):
            self.status_dot.config(fg="#FBBF24")
        elif text.lower() == "ready":
            self.status_dot.config(fg="#34D399")
        elif "missing" in text.lower() or "unavailable" in text.lower() or "no speech" in text.lower():
            self.status_dot.config(fg="#F87171")

    def set_toggle_text(self, text: str) -> None:
        self.toggle_button.config(text=text)

    def run(self) -> None:
        self.root.mainloop()
