import logging
import os
import sys
import threading
from pytool.push_logs import SentToBrowser
from pytool.event import ui_ready_event
if sys.platform == "darwin":
    os.environ.setdefault("WEBKIT_DISABLE_COMPOSITING_MODE", "1")

from pytool.settings import get_log_path
import webview
from dotenv import load_dotenv

from pytool.js_api import JSAPI
from pytool.paths import app_root, is_frozen, resource_dir, ui_index
from pytool.static_server import StaticServer

logger = logging.getLogger("pytool")
UI_READY_TIMEOUT_SECONDS = 10


def setup_logging() -> None:
    if logger.handlers:
        return
    log_path = get_log_path()
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(pathname)s:%(lineno)d "
        "%(funcName)s: %(message)s"))
    logger.setLevel(logging.WARNING)
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
    return ""


def _start_ui_server() -> StaticServer:
    index = ui_index()
    if not index.is_file():
        raise FileNotFoundError(
            f"UI build not found: {index}. "
            "Run the frontend build before packaging."
        )
    server = StaticServer(index.parent)
    server.start()
    return server


def main_logic(window) -> None:
    if not ui_ready_event.wait(timeout=UI_READY_TIMEOUT_SECONDS):
        logger.error(
            "UI did not signal ready within %s seconds; skipping initial log message",
            UI_READY_TIMEOUT_SECONDS,
        )
        return
    sent_to_browser = SentToBrowser(window)
    sent_to_browser.pushMessage(message="App initialized")


def run() -> None:
    setup_logging()
    env = _env_name()
    if not is_frozen():
        load_dotenv(dotenv_path=resource_dir() / f".env.{env}")

    js_api = JSAPI()
    server = None
    try:
        if env == "development" and not is_frozen():
            target = _ui_target(env)
        else:
            server = _start_ui_server()
            target = server.url

        window = webview.create_window(
            "Automation_tool" if env != "development" else "webview_dev",
            target,
            js_api=js_api,
            easy_drag=False,
            resizable=True,
            min_size=(800, 600),
        )

        js_api.set_window(window)
        if sys.platform == "darwin":
            webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
        webview.start(
            func=main_logic,
            args=(window,),
            debug=(
                env == "development" and not is_frozen()))
    finally:
        if server is not None:
            server.stop()


if __name__ == "__main__":
    run()
