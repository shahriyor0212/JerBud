from __future__ import annotations

from typing import Optional

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional in some environments
    np = None


class SpeechToTextEngine:
    def __init__(self, model_size: str = "tiny", language: str = "en") -> None:
        self.model_size = model_size
        self.language = language
        self._model: Optional[object] = None

    def _load_model(self) -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:  # pragma: no cover - package is optional in tests
            raise RuntimeError(
                "faster-whisper is required for speech-to-text. Install the project dependencies first."
            ) from exc

        if self._model is None:
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")

    def _coerce_audio(self, audio: object) -> object:
        if audio is None:
            return np.array([], dtype=np.float32) if np is not None else []

        if np is not None and hasattr(audio, "dtype"):
            arr = np.asarray(audio, dtype=np.float32)
            if arr.ndim > 1:
                arr = arr.reshape(-1)
            return arr

        return audio

    def transcribe(self, audio: object) -> str:
        if np is not None and hasattr(audio, "size"):
            if audio.size == 0:
                return ""
        elif audio is None:
            return ""

        audio = self._coerce_audio(audio)
        self._load_model()
        assert self._model is not None

        segments, _ = self._model.transcribe(
            audio,
            language=self.language,
            beam_size=5,
            word_timestamps=False,
            vad_filter=True,
            without_timestamps=True,
        )
        text = " ".join(segment.text for segment in segments if getattr(segment, "text", "").strip())
        return text.strip()
