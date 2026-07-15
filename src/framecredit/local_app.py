from dataclasses import asdict, dataclass
import errno
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import BinaryIO
from urllib.parse import unquote
import webbrowser

from .processing import (
    ProcessRequest,
    ProcessingError,
    create_attributed_export,
    normalize_x_handle,
)


@dataclass(frozen=True)
class CreatorIdentity:
    x_handle: str = ""


class IdentityStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> CreatorIdentity:
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
            return CreatorIdentity(
                x_handle=str(payload.get("x_handle", "")),
            )
        except (FileNotFoundError, json.JSONDecodeError, OSError, AttributeError):
            return CreatorIdentity()

    def save(self, identity: CreatorIdentity) -> CreatorIdentity:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self._path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(asdict(identity), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary.replace(self._path)
        return identity


def run_local_app(*, port: int, open_browser: bool) -> int:
    store = IdentityStore(_app_home() / "identity.json")
    output_dir = _output_dir()
    handler = _handler_for(store, output_dir)
    try:
        server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError as error:
        if error.errno != errno.EADDRINUSE:
            raise
        print(
            f"framecredit: port {port} is already in use "
            f"(another FrameCredit may be running); "
            f"try: framecredit app --port {port + 1}",
            file=sys.stderr,
        )
        return 1
    actual_port = server.server_address[1]
    url = f"http://127.0.0.1:{actual_port}"
    print(f"FrameCredit local app: {url}", flush=True)
    if open_browser:
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


def _app_home() -> Path:
    override = os.environ.get("FRAMECREDIT_HOME")
    if override:
        return Path(override).expanduser()
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "FrameCredit"
    if os.name == "nt":
        return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "FrameCredit"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "framecredit"


def _output_dir() -> Path:
    override = os.environ.get("FRAMECREDIT_OUTPUT_DIR")
    if override:
        return Path(override).expanduser().resolve()
    return (Path.home() / "Movies" / "FrameCredit").resolve()


def _handler_for(
    store: IdentityStore,
    output_dir: Path,
) -> type[BaseHTTPRequestHandler]:
    class LocalAppHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path in ("/", "/index.html"):
                page = (
                    files("framecredit")
                    .joinpath("static/index.html")
                    .read_text(encoding="utf-8")
                )
                self._send_html(page)
                return
            if self.path == "/api/identity":
                self._send_json(asdict(store.load()))
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_PUT(self) -> None:
            if self.path != "/api/identity":
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            try:
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                identity = CreatorIdentity(
                    x_handle=normalize_x_handle(str(payload["x_handle"])),
                )
                saved = store.save(identity)
            except ProcessingError as error:
                self._send_json(
                    {"error": str(error)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return
            except (
                KeyError,
                TypeError,
                ValueError,
                json.JSONDecodeError,
                OSError,
            ):
                self._send_json(
                    {"error": "x_handle is required"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            self._send_json(asdict(saved))

        def do_POST(self) -> None:
            if self.path.startswith("/api/open/"):
                name = Path(unquote(self.path.removeprefix("/api/open/"))).name
                target = (output_dir / name).resolve()
                if target.parent != output_dir.resolve() or not target.is_file():
                    self._send_json(
                        {"error": "Attributed Export was not found"},
                        status=HTTPStatus.NOT_FOUND,
                    )
                    return
                try:
                    _open_path(target)
                except OSError as error:
                    self._send_json(
                        {"error": str(error)},
                        status=HTTPStatus.BAD_REQUEST,
                    )
                    return
                self._send_json({"opened": str(target)})
                return

            if self.path != "/api/process":
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            identity = store.load()
            if not identity.x_handle:
                self._send_json(
                    {"error": "save the Creator Identity before processing"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                content_length = 0
            if content_length <= 0:
                self._send_json(
                    {"error": "a Source Video is required"},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            filename = unquote(
                self.headers.get("X-FrameCredit-Filename", "source.mp4")
            )
            safe_stem = _safe_stem(filename)
            output = _available_output_path(output_dir, safe_stem)

            try:
                with tempfile.TemporaryDirectory(prefix="framecredit-app-") as temp_dir:
                    source = Path(temp_dir) / "source.mp4"
                    _copy_request_body(self.rfile, source, content_length)
                    created = create_attributed_export(
                        ProcessRequest(
                            source=source,
                            output=output,
                            x_handle=identity.x_handle,
                        )
                    )
            except (OSError, ProcessingError) as error:
                self._send_json(
                    {"error": str(error)},
                    status=HTTPStatus.BAD_REQUEST,
                )
                return

            self._send_json(
                {
                    "output": str(created),
                    "open_url": f"/api/open/{created.name}",
                }
            )

        def _send_html(self, page: str) -> None:
            body = page.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; style-src 'unsafe-inline'; "
                "script-src 'unsafe-inline'; connect-src 'self'; "
                "img-src 'self' data:; media-src 'self' blob:; "
                "object-src 'none'; base-uri 'none'",
            )
            self.end_headers()
            self.wfile.write(body)

        def _send_json(
            self,
            payload: dict[str, str],
            *,
            status: HTTPStatus = HTTPStatus.OK,
        ) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    return LocalAppHandler


def _safe_stem(filename: str) -> str:
    stem = Path(filename).stem
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-._")
    return safe or "video"


def _available_output_path(output_dir: Path, source_stem: str) -> Path:
    first_choice = output_dir / f"{source_stem}-attributed.mp4"
    if not first_choice.exists():
        return first_choice
    suffix = 2
    while True:
        candidate = output_dir / f"{source_stem}-attributed-{suffix}.mp4"
        if not candidate.exists():
            return candidate
        suffix += 1


def _copy_request_body(source: BinaryIO, destination: Path, length: int) -> None:
    remaining = length
    with destination.open("wb") as output:
        while remaining:
            chunk = source.read(min(1024 * 1024, remaining))
            if not chunk:
                raise OSError("the Source Video ended before it was fully received")
            output.write(chunk)
            remaining -= len(chunk)


def _open_path(path: Path) -> None:
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
        return
    opener = (
        shutil.which("open")
        if sys.platform == "darwin"
        else shutil.which("xdg-open")
    )
    if opener is None:
        raise OSError(f"open the file manually: {path}")
    subprocess.Popen(
        [opener, str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
