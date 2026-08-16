from __future__ import annotations

import ctypes
import time
from typing import Optional

try:
    import win32clipboard
    import win32con
except ImportError:  # pragma: no cover - Windows-only dependency
    win32clipboard = None
    win32con = None


class ClipboardPasteService:
    def __init__(self, auto_paste: bool = True) -> None:
        self.auto_paste = auto_paste

    def copy_text(self, text: str) -> None:
        if not text:
            return

        if win32clipboard is None or win32con is None:
            raise RuntimeError("Windows clipboard integration requires pywin32 to be installed.")

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_TEXT)
        win32clipboard.CloseClipboard()

        if self.auto_paste:
            self.paste()

    def paste(self) -> None:
        user32 = ctypes.windll.user32
        user32.keybd_event(0x11, 0, 0, 0)  # VK_CONTROL
        time.sleep(0.02)
        user32.keybd_event(0x56, 0, 0, 0)  # VK_V
        time.sleep(0.02)
        user32.keybd_event(0x56, 0, 0x0002, 0)
        user32.keybd_event(0x11, 0, 0x0002, 0)
