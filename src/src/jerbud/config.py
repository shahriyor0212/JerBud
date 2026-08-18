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
        app_name=d.get("app_name", "Jerbud"),
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
        validate_config(cfg)
        CONFIG_PATH.write_text(json.dumps(asdict(cfg), indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as exc:
        raise RuntimeError("Failed to save configuration") from exc


def _to_bool(value: Any) -> bool:
    """Coerce a config value to a bool, tolerating strings from hand-edited JSON."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def validate_config(cfg: AppConfig) -> AppConfig:
    """Validate and normalize configuration values, tolerating bad types."""
    if isinstance(cfg.hotkey, str):
        cfg.hotkey = cfg.hotkey.strip().lower()
    else:
        cfg.hotkey = "ctrl+shift+alt+s"
    if isinstance(cfg.language, str):
        cfg.language = cfg.language.strip().lower()
    else:
        cfg.language = "en"
    if not isinstance(cfg.mic_index, int) or isinstance(cfg.mic_index, bool) or cfg.mic_index < 0:
        cfg.mic_index = 0
    if isinstance(cfg.stt_model, str):
        cfg.stt_model = cfg.stt_model.strip().lower()
    else:
        cfg.stt_model = "tiny"
    if not isinstance(cfg.app_name, str) or not cfg.app_name.strip():
        cfg.app_name = "Jerbud"
    cfg.auto_paste = _to_bool(cfg.auto_paste)
    cfg.auto_fix_fillers = _to_bool(cfg.auto_fix_fillers)
    cfg.auto_grammar = _to_bool(cfg.auto_grammar)
    return cfg
