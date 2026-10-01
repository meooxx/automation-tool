from curses import window
import logging
import os
import sys
import threading
from pytool.push_logs import SentToBrowser
from pytool.event import ui_ready_event
if sys.platform == "darwin":
    os.environ.setdefault("WEBKIT_DISABLE_COMPOSITING_MODE", "1")

import webview
from dotenv import load_dotenv

from pytool.js_api import JSAPI
from pytool.paths import app_root, is_frozen, resource_dir, ui_index

logger = logging.getLogger("pytool")


def setup_logging() -> None:
    if logger.handlers:
        return
    log_dir = app_root() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(log_dir / "errors.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s: %(message)s"))
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    logger.propagate = False

    def excepthook(exc_type, exc, tb):
        logger.error("unhandled exception", exc_info=(exc_type, exc, tb))
        sys.__excepthook__(exc_type, exc, tb)

    def thread_excepthook(args):
        logger.error(
            "thread exception",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),
        )

    sys.excepthook = excepthook
    threading.excepthook = thread_excepthook


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


def main_logic(window) -> None:
    ui_ready_event.wait()
    sent_to_browser = SentToBrowser(window)
    sent_to_browser.pushMessage(message="App initialized")


def run() -> None:
    setup_logging()
    env = _env_name()
    if not is_frozen():
        load_dotenv(dotenv_path=resource_dir() / f".env.{env}")

    js_api = JSAPI()
    window = webview.create_window(

        "Automation_tool" if env != "development" else "webview_dev",
        _ui_target(env),
        js_api=js_api,
        easy_drag=False,
        resizable=True,
        min_size=(600, 450),
    )

    js_api.set_window(window)
    if sys.platform == "darwin":
        webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
    webview.start(
        func=main_logic,
        args=(window,),
        debug=(
            env == "development" and not is_frozen()))


if __name__ == "__main__":
    run()
