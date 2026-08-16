from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
from typing import Any


CONFIG_PATH = Path.home() / ".jerbud_config.json"


@dataclass
class AppConfig:
    hotkey: str = "ctrl+shift+alt+s"
    language: str = "en"
    mic_index: int = 0
    app_name: str = "Jerbud"
    auto_paste: bool = True
    stt_model: str = "tiny"
    # New options for automatic post-processing
    auto_fix_fillers: bool = False
    auto_grammar: bool = False


def _from_dict(d: dict[str, Any]) -> AppConfig:
    # Provide defaults for missing keys
    return AppConfig(
        hotkey=d.get("hotkey", "ctrl+shift+alt+s"),
        language=d.get("language", "en"),
        mic_index=d.get("mic_index", 0),
        app_name=d.get("app_name", "Shax"),
        auto_paste=d.get("auto_paste", True),
        stt_model=d.get("stt_model", "tiny"),
        auto_fix_fillers=d.get("auto_fix_fillers", False),
        auto_grammar=d.get("auto_grammar", False),
    )


def load_config() -> AppConfig:
    """Load configuration from the user's home directory. Falls back to defaults if missing or invalid."""
    try:
        if CONFIG_PATH.exists():
            with CONFIG_PATH.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return _from_dict(data)
    except Exception:
        # Keep default on any read/parse error
        pass
    return AppConfig()


def save_config(cfg: AppConfig) -> None:
    """Save configuration to the user's home directory as JSON."""
    try:
        CONFIG_PATH.write_text(json.dumps(asdict(cfg), indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        raise
