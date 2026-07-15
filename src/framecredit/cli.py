import argparse
from importlib import metadata
from pathlib import Path
import sys

from .local_app import run_local_app
from .processing import ProcessRequest, ProcessingError, create_attributed_export


def _version() -> str:
    try:
        return metadata.version("framecredit")
    except metadata.PackageNotFoundError:
        return "0+unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="framecredit",
        description="Burn visible creator attribution into a video.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {_version()}"
    )
    commands = parser.add_subparsers(dest="command", required=True)

    process = commands.add_parser(
        "process", help="create an MP4 with a visible Creator Marker"
    )
    process.add_argument("input", type=Path, help="source video")
    process.add_argument("--x-handle", required=True, help="X handle, such as @xiaoming")
    process.add_argument("--output", required=True, type=Path, help="output MP4 path")

    app = commands.add_parser("app", help="open the local drag-and-drop interface")
    app.add_argument("--port", type=int, default=8765, help="local port (default: 8765)")
    app.add_argument(
        "--no-browser",
        action="store_true",
        help="start the local interface without opening a browser",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "process":
        try:
            output = create_attributed_export(
                ProcessRequest(
                    source=args.input,
                    output=args.output,
                    x_handle=args.x_handle,
                )
            )
        except ProcessingError as error:
            print(f"framecredit: {error}", file=sys.stderr)
            return 1

        print(f"Created Attributed Export: {output}")
        return 0

    if args.command == "app":
        return run_local_app(port=args.port, open_browser=not args.no_browser)

    return 2
