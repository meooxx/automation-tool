import json
import logging
from pathlib import Path

from pytool.paths import app_root

logger = logging.getLogger("pytool")


def settings_file() -> Path:
    return app_root() / "config" / "settings.json"


def load_settings() -> dict:
    path = settings_file()
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            logger.error("Settings file is not a JSON object: %s", path)
            return {}
        return data
    except (OSError, json.JSONDecodeError):
        logger.exception("Unable to read settings file: %s", path)
        return {}


def save_settings(data: dict) -> None:
    path = settings_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return True


def get_log_path() -> Path:
    log_path = app_root() / "errors.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)
    return log_path
