from __future__ import annotations

import threading
from typing import Optional

try:
    import numpy as np
    import sounddevice as sd
except ImportError:  # pragma: no cover - dependency is installed at runtime
    np = None  # type: ignore[assignment]
    sd = None  # type: ignore[assignment]


def normalize_audio(audio: object) -> object:
    if np is None:
        return audio

    array = np.asarray(audio, dtype=np.float32)
    if array.size == 0:
        return array
    if array.ndim > 1:
        array = array.reshape(-1)
    return array.astype(np.float32, copy=False)


class AudioRecorder:
    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self._frames: list[object] = []
        self._stream: Optional[object] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        if sd is None or np is None:
            raise RuntimeError("sounddevice and numpy are required to record audio. Install the project dependencies first.")

        self._frames = []
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def _callback(self, indata, frames, time_info, status) -> None:  # type: ignore[no-untyped-def]
        if status:
            print(status)
        with self._lock:
            self._frames.append(np.asarray(indata, dtype=np.float32).copy())

    def stop(self) -> object:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        if not self._frames:
            return np.array([], dtype=np.float32) if np is not None else np.array([], dtype=np.float32)

        with self._lock:
            audio = np.concatenate(self._frames, axis=0) if np is not None else self._frames
            self._frames = []
        return normalize_audio(audio)
