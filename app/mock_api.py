from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread


class _Handler(BaseHTTPRequestHandler):
    data_path: Path
    endpoint: str

    def do_GET(self) -> None:  # noqa: N802
        if self.path != self.endpoint:
            self.send_response(404)
            self.end_headers()
            return
        try:
            payload = self.data_path.read_text(encoding="utf-8")
            json.loads(payload)  # verify before serving
            body = payload.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception:
            self.send_response(500)
            self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        return


def start_mock_api(data_path: str | Path, host: str, port: int, endpoint: str):
    """Start a local REST API in a background thread and return server/thread."""
    data_path = Path(data_path)
    handler = type("MockStudentHandler", (_Handler,), {
        "data_path": data_path,
        "endpoint": endpoint,
    })
    server = ThreadingHTTPServer((host, port), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread
