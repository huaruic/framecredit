import argparse
from pathlib import Path
import sys

from .processing import ProcessRequest, ProcessingError, create_attributed_export


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="framecredit",
        description="Burn visible creator attribution into a video.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    process = commands.add_parser(
        "process", help="create an MP4 with a visible Creator Marker"
    )
    process.add_argument("input", type=Path, help="source video")
    process.add_argument("--creator-name", required=True, help="X display name")
    process.add_argument("--x-handle", required=True, help="X handle, such as @xiaoming")
    process.add_argument("--output", required=True, type=Path, help="output MP4 path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "process":
        try:
            output = create_attributed_export(
                ProcessRequest(
                    source=args.input,
                    output=args.output,
                    creator_name=args.creator_name,
                    x_handle=args.x_handle,
                )
            )
        except ProcessingError as error:
            print(f"framecredit: {error}", file=sys.stderr)
            return 1

        print(f"Created Attributed Export: {output}")
        return 0

    return 2
