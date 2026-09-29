import json

from pytool.paths import app_root


def settings_file():
    return app_root() / "config" / "settings.json"


def load_settings() -> dict:
    path = settings_file()
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_settings(data: dict) -> None:
    path = settings_file()

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return True
