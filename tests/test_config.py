import unittest

import numpy as np

from jerbud.config import AppConfig, load_config
from jerbud.hotkey_listener import HotkeyListener
from jerbud.stt import SpeechToTextEngine


class ConfigTests(unittest.TestCase):
    def test_default_config(self):
        config = load_config()
        self.assertIsInstance(config, AppConfig)
        self.assertEqual(config.hotkey, "ctrl+shift+alt+s")
        self.assertEqual(config.language, "en")

    def test_hotkey_normalization(self):
        self.assertEqual(HotkeyListener.normalize_hotkey("ctrl+shift+alt+s"), "<ctrl>+<shift>+<alt>+s")

    def test_empty_audio_transcription_is_empty(self):
        engine = SpeechToTextEngine()
        empty = np.array([], dtype=np.float32)
        self.assertEqual(engine.transcribe(empty), "")


if __name__ == "__main__":
    unittest.main()
