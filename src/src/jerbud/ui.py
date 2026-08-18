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

# Sentinel color used only for transparency (never rendered as-is).
TRANSPARENT = "#010101"

RADIUS = 14
ANIM_STEP = 16  # ms per animation frame
ANIM_STEPS = 10


def _interpolate(c1: str, c2: str, t: float) -> str:
    """Linearly interpolate between two hex colors; t in [0, 1]."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = round(r1 + (r2 - r1) * t)
    g = round(g1 + (g2 - g1) * t)
    b = round(b1 + (b2 - b1) * t)
    return f"#{r:02X}{g:02X}{b:02X}"


def _lighten(color: str, amount: float = 0.12) -> str:
    return _interpolate(color, "#FFFFFF", amount)


def _darken(color: str, amount: float = 0.12) -> str:
    return _interpolate(color, "#000000", amount)


def _draw_rounded_rect(canvas: tk.Canvas, x1: int, y1: int, x2: int, y2: int, r: int, **kwargs):
    """Draw a rounded rectangle polygon with smooth corners."""
    if r > min(x2 - x1, y2 - y1) / 2:
        r = min(x2 - x1, y2 - y1) // 2
    points = [
        x1 + r, y1,
        x2 - r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1 + r,
        x1, y1,
        x1 + r, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class RoundedButton(tk.Canvas):
    """A modern flat button with rounded corners, hover transition and press feedback."""

    def __init__(
        self,
        master: tk.Widget,
        text: str,
        command=None,
        bg: str = PRIMARY,
        fg: str = "white",
        hover_bg: str | None = None,
        pressed_bg: str | None = None,
        height: int = 36,
        radius: int = 10,
        font=("Segoe UI", 9, "bold"),
        cursor: str = "hand2",
        **kwargs,
    ) -> None:
        super().__init__(
            master,
            bg=TRANSPARENT,
            highlightthickness=0,
            bd=0,
            cursor=cursor,
            **kwargs,
        )
        self._bg = bg
        self._hover_bg = hover_bg or _lighten(bg)
        self._pressed_bg = pressed_bg or _darken(bg)
        self._fg = fg
        self._text = text
        self._font = font
        self._radius = radius
        self._command = command
        self._rect_id = None
        self._text_id = None
        self._anim = None
        self._anim_step = 0
        self._enabled = True

        self.bind("<Configure>", self._redraw)
        self.bind("<Enter>", self._animate_to(self._hover_bg))
        self.bind("<Leave>", self._animate_to(self._bg))
        self.bind("<ButtonPress-1>", self._animate_to(self._pressed_bg))
        self.bind("<ButtonRelease-1>", self._on_release)

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self._redraw()

    def _fill(self) -> str:
        if not self._enabled:
            return _darken(self._bg, 0.55)
        try:
            return self.itemcget(self._rect_id, "fill")
        except (tk.TclError, TypeError):
            return self._bg

    def _animate_to(self, target: str):
        def handler(_event=None) -> None:
            if not self._enabled:
                self._set_fill(_darken(self._bg, 0.55))
                return
            if self._anim:
                self.after_cancel(self._anim)
                self._anim = None
            start = self._fill()
            self._anim_step = 0

            def tick() -> None:
                self._anim_step += 1
                t = self._anim_step / ANIM_STEPS
                self._set_fill(_interpolate(start, target, t))
                if self._anim_step < ANIM_STEPS:
                    self._anim = self.after(ANIM_STEP, tick)
                else:
                    self._anim = None

            self._anim = self.after(ANIM_STEP, tick)

        return handler

    def _set_fill(self, color: str) -> None:
        if self._rect_id is not None:
            self.itemconfig(self._rect_id, fill=color)

    def _on_release(self, event) -> None:
        self._animate_to(self._bg)(event)
        if self._command and self._enabled and 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
            self._command()

    def set_text(self, text: str) -> None:
        self._text = text
        if self._text_id is not None:
            self.itemconfig(self._text_id, text=text)

    def _redraw(self, _event=None) -> None:
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4 or h < 4:
            return
        self.delete("all")
        fill = _darken(self._bg, 0.55) if not self._enabled else self._bg
        fg = "#64748B" if not self._enabled else self._fg
        self._rect_id = _draw_rounded_rect(self, 1, 1, w - 1, h - 1, self._radius, fill=fill, outline="")
        self._text_id = self.create_text(w / 2, h / 2, text=self._text, fill=fg, font=self._font)


class _RoundedPanel(tk.Canvas):
    """Canvas that draws the rounded backdrop for a borderless window."""

    def __init__(self, master: tk.Widget, **kwargs) -> None:
        super().__init__(master, bg=TRANSPARENT, highlightthickness=0, bd=0, **kwargs)
        self._radius = RADIUS
        self.bind("<Configure>", self._redraw)

    def _redraw(self, _event=None) -> None:
        self.delete("panel")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4 or h < 4:
            return
        _draw_rounded_rect(self, 1, 1, w - 1, h - 1, self._radius, fill=DARK, outline="", tags="panel")


def _fade_in(window: tk.Toplevel | tk.Tk) -> None:
    """Animate window opacity from 0 to 1."""
    try:
        window.attributes("-alpha", 0.0)
    except tk.TclError:
        return
    for i in range(1, 11):
        window.after(i * ANIM_STEP, lambda v=i / 10: window.attributes("-alpha", v))


class TinyWindow:
    def __init__(self, app: object, title: str = "Jerbud") -> None:
        self.app = app
        self.root = tk.Tk()
        self.root.title(title)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT)
        try:
            self.root.attributes("-transparentcolor", TRANSPARENT)
        except tk.TclError:
            # Fall back to a plain background on platforms without transparency
            self.root.configure(bg=DARK)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = 340
        height = 214
        x = (screen_width // 2) - (width // 2)
        y = screen_height - height - 28
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        PAD = 10
        self._panel = _RoundedPanel(self.root)
        self._panel.pack(fill="both", expand=True)

        outer = tk.Frame(self.root, bg=DARK)
        self._panel.create_window(
            PAD, PAD, anchor="nw", window=outer, width=width - 2 * PAD, height=height - 2 * PAD
        )

        header = tk.Frame(outer, bg=DARK)
        header.pack(fill="x")

        brand = tk.Label(
            header,
            text=title,
            fg=TEXT,
            bg=DARK,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        brand.pack(side="left")

        self.exit_button = RoundedButton(
            header,
            text="\u00d7",
            command=self.exit_app,
            bg=SURFACE,
            fg=TEXT,
            hover_bg="#2B2F36",
            height=24,
            width=26,
            radius=7,
            font=("Segoe UI", 12, "bold"),
        )
        self.exit_button.pack(side="right")

        # Allow dragging the window by its header (overrideredirect windows need custom drag)
        def _start_move(event):
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
                self.root.geometry(
                    f"{self.root.winfo_width()}x{self.root.winfo_height()}+{new_x}+{new_y}"
                )
            except Exception:
                pass

        header.bind("<ButtonPress-1>", _start_move)
        header.bind("<B1-Motion>", _do_move)
        brand.bind("<ButtonPress-1>", _start_move)
        brand.bind("<B1-Motion>", _do_move)

        self.status_var = tk.StringVar(value="Ready")
        status_row = tk.Frame(outer, bg=DARK)
        status_row.pack(fill="x", pady=(10, 2))

        self.status_dot = tk.Label(
            status_row,
            text="\u25cf",
            fg=STATUS_READY,
            bg=DARK,
            font=("Segoe UI", 12),
        )
        self.status_dot.pack(side="left", padx=(0, 8))

        self.status_label = tk.Label(
            status_row,
            textvariable=self.status_var,
            fg=TEXT,
            bg=DARK,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        hotkey_hint = tk.Label(
            outer,
            text=f"Press {self.app.config.hotkey} to toggle",
            fg=MUTED,
            bg=DARK,
            font=("Segoe UI", 8),
            anchor="w",
        )
        hotkey_hint.pack(fill="x", pady=(0, 8))

        controls = tk.Frame(outer, bg=DARK)
        controls.pack(fill="x")

        self.listen_button = RoundedButton(
            controls,
            text="Listen",
            command=self.app.start_recording,
            bg=PRIMARY,
            fg="white",
        )
        self.listen_button.pack(side="left", expand=True, fill="x")

        self.stop_button = RoundedButton(
            controls,
            text="Stop",
            command=self.app.stop_recording,
            bg=STATUS_ERROR,
            fg="white",
            hover_bg="#EF4444",
            pressed_bg="#B91C1C",
        )
        self.stop_button.pack(side="left", padx=(8, 0), expand=True, fill="x")

        self.settings_button = RoundedButton(
            controls,
            text="Settings",
            command=self.show_settings,
            bg=SURFACE,
            fg=TEXT,
            hover_bg="#1F2937",
            pressed_bg="#1A1C20",
        )
        self.settings_button.pack(side="left", padx=(8, 0), expand=True, fill="x")

        caption = tk.Label(
            outer,
            text="Audio is processed locally on this computer",
            fg=MUTED,
            bg=DARK,
            font=("Segoe UI", 8),
            anchor="w",
        )
        caption.pack(fill="x", pady=(8, 0))

        self._pulsing = False
        self._pulse_id = None
        self.root.bind("<Escape>", lambda *_: self.exit_app())

        # Start with the Stop button disabled
        self.stop_button.set_enabled(False)

        # Entrance animation
        _fade_in(self.root)

    # ---- status & status dot -------------------------------------------------

    def set_status(self, text: str) -> None:
        self.status_var.set(text)
        lower = text.lower()
        if lower.startswith("listening") or lower.startswith("transcribing"):
            self.status_dot.config(fg=STATUS_ACTIVE)
            self._start_pulse()
        elif lower == "ready":
            self._stop_pulse()
            self.status_dot.config(fg=STATUS_READY)
        elif "missing" in lower or "unavailable" in lower or "no speech" in lower:
            self._stop_pulse()
            self.status_dot.config(fg=STATUS_ERROR)
        else:
            self._stop_pulse()
            self.status_dot.config(fg=STATUS_READY)

    def _start_pulse(self) -> None:
        self._stop_pulse()
        shades = [
            STATUS_ACTIVE,
            _lighten(STATUS_ACTIVE, 0.25),
            STATUS_ACTIVE,
            _darken(STATUS_ACTIVE, 0.15),
        ]
        self._pulsing = True
        self._pulse_step = 0

        def tick() -> None:
            if not self._pulsing:
                return
            self.status_dot.config(fg=shades[self._pulse_step % len(shades)])
            self._pulse_step += 1
            self._pulse_id = self.root.after(260, tick)

        tick()

    def _stop_pulse(self) -> None:
        self._pulsing = False
        if self._pulse_id is not None:
            self.root.after_cancel(self._pulse_id)
            self._pulse_id = None

    def set_listening(self, listening: bool) -> None:
        """Enable/disable the Listen and Stop buttons based on recording state."""
        self.listen_button.set_enabled(not listening)
        self.stop_button.set_enabled(listening)

    def set_toggle_text(self, text: str) -> None:
        """Compatibility shim for older app code that toggled a single button label."""
        if hasattr(self, "toggle_button"):
            self.toggle_button.set_text(text)

    # ---- settings ------------------------------------------------------------

    def show_settings(self) -> None:
        cfg = self.app.config
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.transient(self.root)
        win.overrideredirect(True)
        try:
            win.attributes("-transparentcolor", TRANSPARENT)
        except tk.TclError:
            pass
        win.configure(bg=TRANSPARENT)
        win.grab_set()

        W, H = 460, 460
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        win.geometry(f"{W}x{H}+{x}+{y}")
        win.attributes("-topmost", True)

        PAD = 10
        panel = _RoundedPanel(win)
        panel.pack(fill="both", expand=True)

        frame = tk.Frame(win, bg=DARK)
        panel.create_window(
            PAD, PAD, anchor="nw", window=frame, width=W - 2 * PAD, height=H - 2 * PAD
        )

        # Header (drag + close)
        header = tk.Frame(frame, bg=DARK)
        header.pack(fill="x")
        tk.Label(
            header, text="Settings", fg=TEXT, bg=DARK, font=("Segoe UI", 11, "bold")
        ).pack(side="left")

        RoundedButton(
            header,
            text="\u00d7",
            command=win.destroy,
            bg=SURFACE,
            fg=TEXT,
            hover_bg="#2B2F36",
            height=22,
            width=24,
            radius=7,
            font=("Segoe UI", 11, "bold"),
        ).pack(side="right")

        def _start_move(event):
            self._d_win_x = win.winfo_x()
            self._d_win_y = win.winfo_y()
            self._d_evt_x = event.x_root
            self._d_evt_y = event.y_root

        def _do_move(event):
            win.geometry(
                f"{W}x{H}+{self._d_win_x + event.x_root - self._d_evt_x}+"
                f"{self._d_win_y + event.y_root - self._d_evt_y}"
            )

        header.bind("<ButtonPress-1>", _start_move)
        header.bind("<B1-Motion>", _do_move)

        body = tk.Frame(frame, bg=DARK)
        body.pack(fill="both", expand=True, pady=(10, 0))

        # Hotkey
        tk.Label(body, text="Start/Stop hotkey:", fg=TEXT, bg=DARK).pack(anchor="w")
        hotkey_var = tk.StringVar(value=cfg.hotkey)
        hotkey_entry = tk.Entry(
            body, textvariable=hotkey_var, bg=PANEL, fg=TEXT, insertbackground=TEXT,
            relief="flat", highlightthickness=1, highlightbackground=SURFACE,
            highlightcolor=PRIMARY, bd=0,
        )
        hotkey_entry.pack(fill="x", pady=(0, 4), ipady=4)
        tk.Label(
            body, text="Use format: ctrl+alt+shift+s (order: modifiers + key)",
            fg=MUTED, bg=DARK, font=("Segoe UI", 8),
        ).pack(anchor="w")

        # Language
        tk.Label(body, text="Language (ISO code):", fg=TEXT, bg=DARK).pack(anchor="w", pady=(8, 0))
        lang_var = tk.StringVar(value=cfg.language)
        lang_entry = tk.Entry(
            body, textvariable=lang_var, bg=PANEL, fg=TEXT, insertbackground=TEXT,
            relief="flat", highlightthickness=1, highlightbackground=SURFACE,
            highlightcolor=PRIMARY, bd=0,
        )
        lang_entry.pack(fill="x", pady=(4, 0), ipady=4)

        def _checkbox(parent, text, var):
            return tk.Checkbutton(
                parent, text=text, variable=var, fg=TEXT, bg=DARK,
                selectcolor=PANEL, activebackground=DARK, activeforeground=TEXT,
                bd=0, highlightthickness=0, cursor="hand2", font=("Segoe UI", 9),
            )

        # Auto-paste
        auto_paste_var = tk.BooleanVar(value=cfg.auto_paste)
        _checkbox(body, "Auto-paste transcript", auto_paste_var).pack(anchor="w", pady=(8, 0))

        # Automatic corrections: fillers and grammar
        tk.Label(body, text="Automatic post-processing:", fg=TEXT, bg=DARK).pack(anchor="w", pady=(10, 0))
        fix_fillers_var = tk.BooleanVar(value=getattr(cfg, "auto_fix_fillers", False))
        grammar_var = tk.BooleanVar(value=getattr(cfg, "auto_grammar", False))
        _checkbox(body, "Remove common filler words (uh, umm, like)", fix_fillers_var).pack(anchor="w")
        _checkbox(body, "Light grammar correction", grammar_var).pack(anchor="w")

        # Help / recommendation text (compact) + more button
        help_frame = tk.Frame(body, bg=DARK)
        help_frame.pack(fill="x", pady=(8, 0))
        tk.Label(help_frame, text="Recommendation:", fg=TEXT, bg=DARK).pack(anchor="w")
        tk.Label(
            help_frame,
            text="Audio is processed locally on your computer. For corrections, start with filler removal, then an optional light grammar pass.",
            fg=MUTED, bg=DARK, wraplength=400, justify="left",
        ).pack(anchor="w")

        def show_recommendation() -> None:
            messagebox.showinfo(
                "Auto-corrections recommendation",
                (
                    "Jerbud runs fully locally - audio and transcripts stay on your computer.\n\n"
                    "1) 'Remove common filler words' - a fast, deterministic pass that strips 'uh', 'umm', "
                    "'like', and similar fillers. Safe to leave enabled.\n\n"
                    "2) 'Light grammar correction' - an optional pass that smooths grammar. "
                    "Kept separate so you can enable it only when needed.\n\n"
                    "Both options run on-device; nothing is sent to a server.",
                ),
            )

        RoundedButton(
            help_frame,
            text="More...",
            command=show_recommendation,
            bg=SURFACE,
            fg=TEXT,
            hover_bg="#1F2937",
            height=24,
            radius=8,
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="e", pady=(6, 0))

        # Buttons
        btn_frame = tk.Frame(frame, bg=DARK)
        btn_frame.pack(fill="x", pady=(12, 0))

        def restore_defaults() -> None:
            hotkey_var.set("ctrl+shift+alt+s")
            lang_var.set("en")
            auto_paste_var.set(True)
            fix_fillers_var.set(False)
            grammar_var.set(False)

        def apply_changes(save: bool = False) -> None:
            cfg.hotkey = hotkey_var.get().strip() or cfg.hotkey
            cfg.language = lang_var.get().strip() or cfg.language
            cfg.auto_paste = bool(auto_paste_var.get())
            setattr(cfg, "auto_fix_fillers", bool(fix_fillers_var.get()))
            setattr(cfg, "auto_grammar", bool(grammar_var.get()))

            try:
                save_config(cfg)
            except Exception as exc:
                messagebox.showwarning("Save failed", f"Failed to save settings: {exc}")

            try:
                self.app.apply_config()
            except Exception:
                messagebox.showinfo("Applied", "Settings updated \u2014 restart app if changes are not active.")

            if save:
                win.destroy()

        RoundedButton(
            btn_frame, text="Restore defaults", command=restore_defaults,
            bg=SURFACE, fg=TEXT, hover_bg="#1A1C20", height=30, radius=9,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left")

        RoundedButton(
            btn_frame, text="Cancel", command=win.destroy,
            bg=SURFACE, fg=TEXT, hover_bg="#1A1C20", height=30, radius=9,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right")

        RoundedButton(
            btn_frame, text="Apply", command=lambda: apply_changes(save=False),
            bg=PRIMARY, fg="white", height=30, radius=9,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right", padx=(0, 6))

        RoundedButton(
            btn_frame, text="Save & Close", command=lambda: apply_changes(save=True),
            bg=ACCENT, fg="white", height=30, radius=9,
            font=("Segoe UI", 9, "bold"),
        ).pack(side="right", padx=(0, 6))

        win.bind("<Escape>", lambda *_: win.destroy())
        _fade_in(win)
        win.wait_window()

    def exit_app(self) -> None:
        self.app.stop()

    def run(self) -> None:
        self.root.mainloop()
