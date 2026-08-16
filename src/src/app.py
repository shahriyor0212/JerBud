from __future__ import annotations

import logging
import threading
import tkinter as tk
from tkinter import messagebox

from .audio import AudioRecorder
from .config import AppConfig, validate_config
from .hotkey_listener import HotkeyListener
from .paste import ClipboardPasteService
from .stt import SpeechToTextEngine
from .ui import TinyWindow

# Optional post-processing import
try:
    from .postprocess import remove_fillers
except Exception as _postprocess_import_exc:  # pragma: no cover - optional module
    remove_fillers = None
    _postprocess_import_error = _postprocess_import_exc
else:
    _postprocess_import_error = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class App:
    def __init__(self, config: AppConfig) -> None:
        # Validate config early to catch bad values before starting anything
        self.config = validate_config(config)

        self.auto_paste = self.config.auto_paste
        self.listening = False

        # Hotkey listener
        self.listener = HotkeyListener(self.config.hotkey, self.toggle_recording)
        self.recorder = AudioRecorder()
        self.stt = SpeechToTextEngine(
            model_size=self.config.stt_model, language=self.config.language
        )
        self.clipboard = ClipboardPasteService(auto_paste=self.auto_paste)
        self.ui = TinyWindow(self, title=self.config.app_name)

        # Initialize UI
        self.ui.set_status("Ready")
        self.ui.set_toggle_text("Listen")

    def apply_config(self) -> None:
        """Apply configuration changes at runtime with proper error handling."""
        try:
            # Update basic flags
            self.auto_paste = self.config.auto_paste

            # Recreate clipboard service with new auto_paste setting
            try:
                self.clipboard = ClipboardPasteService(auto_paste=self.auto_paste)
            except Exception as exc:
                logger.warning("Failed to reinitialize clipboard service: %s", exc)

            # Recreate STT engine if language or model changed
            try:
                self.stt = SpeechToTextEngine(
                    model_size=self.config.stt_model, language=self.config.language
                )
            except Exception as exc:
                logger.warning("Failed to reinitialize speech engine: %s", exc)

            # Recreate hotkey listener if hotkey changed
            try:
                # Stop existing listener
                if getattr(self, "listener", None) is not None:
                    try:
                        self.listener.stop()
                    except Exception:
                        pass

                self.listener = HotkeyListener(self.config.hotkey, self.toggle_recording)
                try:
                    self.listener.start()
                except Exception as exc:
                    logger.warning("Failed to start hotkey listener: %s", exc)
            except Exception as exc:
                logger.error("Failed to update hotkey listener: %s", exc)

            # Update window title if changed
            try:
                self.ui.root.title(self.config.app_name)
            except Exception:
                pass

        except Exception as exc:
            # Log unexpected errors but do not crash the UI
            logger.exception("Unexpected error during config reload: %s", exc)

    def _update_ui_status(self, text: str, status_dot_color: str = "#34D399") -> None:
        """Thread‑safe UI status update."""
        def _update():
            self.ui.set_status(text)
            if text.lower().startswith("listening") or text.lower().startswith("transcribing"):
                self.ui.status_dot.config(fg="#FBBF24")
            elif text.lower() == "ready":
                self.ui.status_dot.config(fg="#34D399")
            elif "missing" in text.lower() or "unavailable" in text.lower() or "no speech" in text.lower():
                self.ui.status_dot.config(fg="#F87171")
            else:
                # Default colour
                self.ui.status_dot.config(fg=status_dot_color)
        # Schedule on the UI thread
        self.ui.root.after(0, _update)

    def toggle_recording(self) -> None:
        if self.listening:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self) -> None:
        self.listening = True
        try:
            self.recorder.start()
        except RuntimeError as exc:
            self.listening = False
            self._update_ui_status("Mic unavailable")
            logger.error("Mic start error: %s", exc)
            return

        self._update_ui_status("Listening...")
        # UI text change must be done on UI thread
        self.ui.root.after(0, lambda: self.ui.set_toggle_text("Stop"))

    def stop_recording(self) -> None:
        if not self.listening:
            return

        self.listening = False
        self._update_ui_status("Transcribing...")
        audio = self.recorder.stop()

        try:
            text = self.stt.transcribe(audio)
        except RuntimeError as exc:
            self._update_ui_status("Speech model missing")
            logger.error("Transcription error: %s", exc)
            return

        # Post‑process transcript according to user settings
        if text:
            if getattr(self.config, "auto_fix_fillers", False):
                if remove_fillers is not None:
                    try:
                        text = remove_fillers(text)
                    except Exception as exc:
                        logger.warning("Filler removal failed: %s", exc)
                else:
                    logger.warning("Filler removal unavailable: %s", _postprocess_import_error)

            # Future grammar correction could be added here
            # if getattr(self.config, "auto_grammar", False):
            #     text = grammar_correct(text)

            try:
                self.clipboard.copy_text(text)
                self._update_ui_status("Ready")
            except RuntimeError as exc:
                self._update_ui_status("Clipboard unavailable")
                logger.error("Clipboard error: %s", exc)
        else:
            self._update_ui_status("No speech detected")

    def run(self) -> None:
        logger.info("Starting %s (hotkey: %s)", self.config.app_name, self.config.hotkey)
        self.listener.start()
        self.ui.run()

    def stop(self) -> None:
        logger.info("Shutting down %s", self.config.app_name)
        self.listener.stop()
        if self.listening:
            self.recorder.stop()
        self.ui.root.destroy()
        logger.info("Stopped %s", self.config.app_name)


if __name__ == "__main__":
    # This entry point is kept for backward compatibility.
    # The main entry point is now in `src/jerbud/app.py` → Application class.
    pass