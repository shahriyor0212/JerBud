# Jerbud

Jerbud is a minimal, free, local dictation utility for Windows. It listens for a global hotkey, captures microphone input, and pastes the transcribed text into the currently focused app.

## Current status

This scaffold is intentionally minimal and is set up for review before expanding the app.

## Project goals

- Fully free and local-first
- Python based
- No database in the MVP
- One hotkey to start/stop listening
- Paste into the active application window
- Minimal UI with tray or small settings window

## Suggested stack

- Python 3.10+
- `pynput` for global hotkeys
- `faster-whisper` for local speech-to-text
- `sounddevice` for microphone capture
- `pywin32` for Windows integration and paste behavior

## Run

```bash
python -m main
```

## Automatic corrections

Jerbud can optionally post-process transcripts to remove filler words (e.g. "uh", "umm") and perform light grammar corrections. Both options run on-device with no extra dependencies:

1) **Remove common filler words** — a deterministic, rule-based pass that strips repeated filler tokens ("uh", "umm", "like", "you know", "I mean") and tidies spacing/punctuation.

2) **Light grammar correction** — a conservative rule-based pass that restores common apostrophes ("cant" → "can't"), capitalizes standalone "i" and sentence starts, and ensures sentences end with punctuation. It intentionally avoids large-scale rewrites.

Both are toggled independently in the settings window. All processing is on-device: audio and transcripts never leave your computer.

## Directory layout

- `src/jerbud/` — application package
- `tests/` — smoke tests
