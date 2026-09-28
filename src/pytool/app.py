import os
import sys

import webview
from dotenv import load_dotenv

from pytool.js_api import JSAPI
from pytool.paths import is_frozen, resource_dir, ui_index


def _env_name() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1].lower()
    if is_frozen():
        return "production"
    return os.getenv("APP_ENV", "production").lower()


def _ui_target(env: str) -> str:
    if env == "development" and not is_frozen():
        url = os.getenv("UI_URL", "http://localhost:3000")
        return url
    index = ui_index()
    if not index.is_file():
        raise FileNotFoundError(
            f"UI build not found: {index}. Run the frontend build before packaging."
        )
    return str(index)


def run() -> None:
    env = _env_name()
    if not is_frozen():
        load_dotenv(dotenv_path=resource_dir() / f".env.{env}")

    js_api = JSAPI()
    window = webview.create_window(
        "tool_ui" if env != "development" else "webview_dev",
        _ui_target(env),
        js_api=js_api,
        easy_drag=False,
        resizable=True,
    )
    js_api.set_window(window)
    webview.start(debug=(env == "development" and not is_frozen()))


if __name__ == "__main__":
    run()
