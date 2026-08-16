from __future__ import annotations

from typing import Callable, Optional


class HotkeyListener:
    """Hotkey listener that supports keyboard GlobalHotKeys and a custom
    Ctrl + mouse-side-button combination.

    The hotkey string supports the usual modifiers (ctrl, alt, shift, cmd)
    and either a keyboard key or a mouse token: "mouse_x1" or "mouse_x2".

    Examples:
      - "ctrl+shift+alt+s" (keyboard GlobalHotKeys)
      - "ctrl+mouse_x1" (Ctrl + mouse side/back button)
      - "ctrl+mouse_x2" (Ctrl + mouse side/forward button)
    """

    def __init__(self, hotkey: str, on_activate: Callable[[], None]) -> None:
        self.hotkey = hotkey
        self.on_activate = on_activate
        self._listener: Optional[object] = None
        # When using the custom combined listener, store the keyboard and mouse listeners
        self._keyboard_listener: Optional[object] = None
        self._mouse_listener: Optional[object] = None
        self._pressed_mods: set[str] = set()
        self._pressed_keys: set[str] = set()
        self._pressed_mouse: set[str] = set()
        self._activated: bool = False

    @staticmethod
    def normalize_hotkey(hotkey: str) -> str:
        parts = [part.strip().lower() for part in hotkey.split('+') if part.strip()]
        normalized = []
        for part in parts:
            if part in {"ctrl", "alt", "shift", "cmd", "super", "meta", "win"}:
                normalized.append(f"<{part}>")
            else:
                # preserve mouse tokens as-is (e.g. mouse_x1)
                normalized.append(part)
        return "+".join(normalized)

    def start(self) -> None:
        try:
            from pynput import keyboard, mouse
        except ImportError as exc:  # pragma: no cover - environment dependency
            raise RuntimeError(
                "pynput is required for the hotkey listener. Install project dependencies first."
            ) from exc

        if self._listener is not None or self._keyboard_listener is not None or self._mouse_listener is not None:
            return

        # Parse hotkey
        parts = [p.strip().lower() for p in self.hotkey.split('+') if p.strip()]
        modifiers = {p for p in parts if p in {"ctrl", "alt", "shift", "cmd", "super", "meta", "win"}}
        mouse_parts = {p for p in parts if p in {"mouse_x1", "mouse_x2", "x1", "x2", "button_x1", "button_x2"}}
        key_parts = [p for p in parts if p not in modifiers and p not in mouse_parts]

        # Normalize mouse token names
        normalized_mouse = set()
        for m in mouse_parts:
            if m in {"mouse_x1", "x1", "button_x1"}:
                normalized_mouse.add("x1")
            else:
                normalized_mouse.add("x2")

        # If mouse button is part of the hotkey, use a combined keyboard+mouse listener
        if normalized_mouse:
            # Custom combined listener
            self._setup_combined_listener(modifiers, normalized_mouse)
            return

        # Otherwise, fallback to GlobalHotKeys for pure keyboard combos
        normalized = self.normalize_hotkey(self.hotkey)
        # GlobalHotKeys expects strings like "<ctrl>+<alt>+s"
        self._listener = keyboard.GlobalHotKeys({normalized: self.on_activate})
        self._listener.start()

    def _setup_combined_listener(self, modifiers: set[str], mouse_buttons: set[str]) -> None:
        """Start keyboard and mouse listeners and trigger activation when the
        configured modifiers are down and a matching mouse side button is pressed.
        """
        from pynput import keyboard, mouse

        required_mods = set(modifiers)
        required_mouse = set(mouse_buttons)

        # Helper to map pynput keys to our modifier names
        def _key_to_name(key) -> Optional[str]:
            try:
                # Special keys (ctrl, alt, shift, etc.)
                if key in (keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                    return "ctrl"
                if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                    return "alt"
                if key in (keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r):
                    return "shift"
                if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r, keyboard.Key.alt_gr):
                    return "cmd"
            except Exception:
                pass
            # Normal character keys
            try:
                if hasattr(key, "char") and key.char:
                    return key.char.lower()
            except Exception:
                pass
            return None

        def on_key_press(key):
            name = _key_to_name(key)
            if name in {"ctrl", "alt", "shift", "cmd"}:
                self._pressed_mods.add(name)
            else:
                if name:
                    self._pressed_keys.add(name)

        def on_key_release(key):
            name = _key_to_name(key)
            if name in {"ctrl", "alt", "shift", "cmd"}:
                self._pressed_mods.discard(name)
                # Changing modifiers should clear activation so a new press is required
                self._activated = False
            else:
                if name:
                    self._pressed_keys.discard(name)

        def _button_name(btn: mouse.Button) -> Optional[str]:
            # Map mouse.Button.x1/x2 to x1/x2
            if btn == mouse.Button.x1:
                return "x1"
            if btn == mouse.Button.x2:
                return "x2"
            return None

        def on_click(x, y, button, pressed):
            name = _button_name(button)
            if not name:
                return
            if pressed:
                self._pressed_mouse.add(name)
                # Activation condition: required modifiers present and required mouse present
                if required_mouse.issubset(self._pressed_mouse) and required_mods.issubset(self._pressed_mods):
                    if not self._activated:
                        try:
                            self.on_activate()
                        finally:
                            # Prevent repeated triggers until the button is released
                            self._activated = True
            else:
                # On release, clear pressed state and allow future activations
                self._pressed_mouse.discard(name)
                self._activated = False

        # Start listeners
        self._keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
        self._mouse_listener = mouse.Listener(on_click=on_click)
        self._keyboard_listener.start()
        self._mouse_listener.start()

    def stop(self) -> None:
        # Stop GlobalHotKeys listener
        if self._listener is not None:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None

        # Stop keyboard listener
        if self._keyboard_listener is not None:
            try:
                self._keyboard_listener.stop()
            except Exception:
                pass
            self._keyboard_listener = None

        # Stop mouse listener
        if self._mouse_listener is not None:
            try:
                self._mouse_listener.stop()
            except Exception:
                pass
            self._mouse_listener = None

        # Clear pressed state
        self._pressed_mods.clear()
        self._pressed_keys.clear()
        self._pressed_mouse.clear()
        self._activated = False
