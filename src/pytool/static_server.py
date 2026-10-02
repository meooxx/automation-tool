from __future__ import annotations

import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


class _SPARequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str, **kwargs):
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        file_path = Path(self.translate_path(path))
        if not file_path.exists() and "." not in Path(path).name:
            query = urlsplit(self.path).query
            self.path = "/index.html" + (f"?{query}" if query else "")
        super().do_GET()

    def log_message(self, format: str, *args) -> None:
        return


class StaticServer:
    def __init__(self, root: Path):
        self._root = root
        self._server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            lambda *args, **kwargs: _SPARequestHandler(
                *args, directory=str(self._root), **kwargs
            ),
        )
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="pytool-static-server",
            daemon=True,
        )

    @property
    def url(self) -> str:
        host, port = self._server.server_address
        return f"http://{host}:{port}/"

    def start(self) -> str:
        self._thread.start()
        return self.url

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)
