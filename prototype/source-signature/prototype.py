#!/usr/bin/env python3
"""PROTOTYPE — render and inspect a simple distributed Source Signature."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from PIL import Image, ImageDraw, ImageFont

from source_signature import SourceSignaturePlan, build_plan


DURATION = 12.0
WIDTH = 1280
HEIGHT = 720
FPS = 24
VARIANT_ORDER = ("attributed", "reencoded", "cropped", "captioned")
FONT_CANDIDATES = (
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
)


@dataclass
class PrototypeState:
    status: str = "not generated"
    selected_index: int = 0
    artifacts: dict[str, Path] = field(default_factory=dict)
    probes: dict[str, dict[str, object]] = field(default_factory=dict)
    contact_sheet: Path | None = None
    output_dir: Path | None = None

    @property
    def selected_name(self) -> str:
        return VARIANT_ORDER[self.selected_index]


def require_tools() -> None:
    missing = [tool for tool in ("ffmpeg", "ffprobe") if shutil.which(tool) is None]
    if missing:
        raise RuntimeError(f"missing required tools: {', '.join(missing)}")


def run(command: list[str]) -> None:
    result = subprocess.run(command, text=True, capture_output=True)
    if result.returncode:
        tail = "\n".join(result.stderr.splitlines()[-30:])
        raise RuntimeError(f"command failed ({result.returncode}): {' '.join(command)}\n{tail}")


def find_font() -> Path:
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            return candidate
    raise RuntimeError("no suitable system font found")


def draw_panel(
    path: Path,
    size: tuple[int, int],
    lines: tuple[tuple[str, int], ...],
    radius: int = 18,
) -> None:
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (1, 1, size[0] - 2, size[1] - 2),
        radius=radius,
        fill=(10, 14, 20, 218),
        outline=(255, 255, 255, 90),
        width=2,
    )
    font_path = find_font()
    fonts = [ImageFont.truetype(str(font_path), font_size) for _, font_size in lines]
    heights = []
    for (text, _), font in zip(lines, fonts):
        box = draw.textbbox((0, 0), text, font=font)
        heights.append(box[3] - box[1])
    total_height = sum(heights) + max(0, len(lines) - 1) * 12
    y = (size[1] - total_height) / 2
    for ((text, _), font, line_height) in zip(lines, fonts, heights):
        box = draw.textbbox((0, 0), text, font=font)
        text_width = box[2] - box[0]
        draw.text(
            ((size[0] - text_width) / 2, y),
            text,
            font=font,
            fill=(255, 255, 255, 255),
            stroke_width=1,
            stroke_fill=(0, 0, 0, 180),
        )
        y += line_height + 12
    image.save(path)


def generate_source(path: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "lavfi",
            "-i",
            f"testsrc2=size={WIDTH}x{HEIGHT}:rate={FPS}",
            "-f",
            "lavfi",
            "-i",
            "sine=frequency=440:sample_rate=48000",
            "-t",
            str(DURATION),
            "-shortest",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(path),
        ]
    )


def marker_position(position: str) -> tuple[str, str]:
    positions = {
        "top_left": ("40", "40"),
        "top_right": ("W-w-40", "40"),
        "center": ("(W-w)/2", "H*0.18"),
    }
    return positions[position]


def between(start: float, end: float) -> str:
    return f"between(t,{start:.3f},{end:.3f})"


def overlay_filter(plan: SourceSignaturePlan) -> str:
    filters: list[str] = []
    marker_count = len(plan.marker_windows)
    card_count = len(plan.card_windows)
    marker_labels = "".join(f"[m{i}]" for i in range(marker_count))
    card_labels = "".join(f"[c{i}]" for i in range(card_count))
    filters.append(f"[1:v]format=rgba,split={marker_count}{marker_labels}")

    current = "0:v"
    for index, window in enumerate(plan.marker_windows):
        x, y = marker_position(window.position)
        output = f"v_marker_{index}"
        filters.append(
            f"[{current}][m{index}]overlay=x={x}:y={y}:enable='{between(window.start, window.end)}'[{output}]"
        )
        current = output

    filters.append(f"[2:v]format=rgba,split={card_count}{card_labels}")
    for index, window in enumerate(plan.card_windows):
        output = "vout" if index == card_count - 1 else f"v_card_{index}"
        filters.append(
            f"[{current}][c{index}]overlay=x=(W-w)/2:y=(H-h)/2:enable='{between(window.start, window.end)}'[{output}]"
        )
        current = output
    return ";".join(filters)


def generate_attributed(
    source: Path,
    marker: Path,
    card: Path,
    output: Path,
    plan: SourceSignaturePlan,
) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(marker),
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(card),
            "-filter_complex",
            overlay_filter(plan),
            "-map",
            "[vout]",
            "-map",
            "0:a?",
            "-t",
            str(plan.duration),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            str(output),
        ]
    )


def generate_reencoded(source: Path, output: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "34",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "80k",
            str(output),
        ]
    )


def generate_cropped(source: Path, output: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-vf",
            "crop=1024:648:128:36,scale=1280:720",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "24",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",
            str(output),
        ]
    )


def generate_captioned(source: Path, caption: Path, output: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(caption),
            "-filter_complex",
            f"[0:v][1:v]overlay=x=(W-w)/2:y=H-h-24:enable='{between(0, DURATION)}'[vout]",
            "-map",
            "[vout]",
            "-map",
            "0:a?",
            "-t",
            str(DURATION),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "24",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            str(output),
        ]
    )


def probe(path: Path) -> dict[str, object]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,codec_name,width,height",
            "-of",
            "json",
            str(path),
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(result.stdout)


def extract_frame(video: Path, timestamp: float, output: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(timestamp),
            "-i",
            str(video),
            "-frames:v",
            "1",
            str(output),
        ]
    )


def generate_contact_sheet(artifacts: dict[str, Path], output_dir: Path) -> Path:
    timestamps = (2.0, 4.5, 8.5, 11.2)
    cell_width, cell_height = 320, 180
    label_height = 28
    sheet = Image.new(
        "RGB",
        (cell_width * len(timestamps), (cell_height + label_height) * len(VARIANT_ORDER)),
        (18, 22, 29),
    )
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(find_font()), 17)
    frame_dir = output_dir / "frames"
    frame_dir.mkdir(exist_ok=True)

    for row, name in enumerate(VARIANT_ORDER):
        for column, timestamp in enumerate(timestamps):
            frame_path = frame_dir / f"{name}-{timestamp:.1f}.png"
            extract_frame(artifacts[name], timestamp, frame_path)
            frame = Image.open(frame_path).convert("RGB").resize((cell_width, cell_height))
            x = column * cell_width
            y = row * (cell_height + label_height) + label_height
            sheet.paste(frame, (x, y))
            label = f"{name} · {timestamp:.1f}s"
            draw.text((x + 8, y - label_height + 4), label, font=font, fill=(240, 244, 250))

    path = output_dir / "contact-sheet.png"
    sheet.save(path)
    return path


def generate_artifacts(
    output_dir: Path,
    plan: SourceSignaturePlan,
    progress: Callable[[str], None] | None = None,
) -> tuple[dict[str, Path], dict[str, dict[str, object]], Path]:
    require_tools()
    output_dir.mkdir(parents=True, exist_ok=True)
    if any(output_dir.iterdir()):
        raise RuntimeError(f"output directory must be empty: {output_dir}")

    def report(message: str) -> None:
        if progress:
            progress(message)

    source = output_dir / "source.mp4"
    marker = output_dir / "creator-marker.png"
    card = output_dir / "source-card.png"
    caption = output_dir / "caption-overlay.png"
    artifacts = {name: output_dir / f"{name}.mp4" for name in VARIANT_ORDER}

    report("rendering overlay assets")
    draw_panel(marker, (500, 72), (("原创：小明  @xiaoming", 30),))
    draw_panel(
        card,
        (860, 210),
        (("原作者：小明  @xiaoming", 42), ("原视频：教学视频标题", 28)),
        radius=24,
    )
    draw_panel(caption, (930, 84), (("搬运版本可能在这里添加自己的字幕", 27),))

    report("generating Source Video")
    generate_source(source)
    report("generating Attributed Export")
    generate_attributed(source, marker, card, artifacts["attributed"], plan)
    report("generating re-encoded rendition")
    generate_reencoded(artifacts["attributed"], artifacts["reencoded"])
    report("generating lightly cropped rendition")
    generate_cropped(artifacts["attributed"], artifacts["cropped"])
    report("generating caption-overlay rendition")
    generate_captioned(artifacts["attributed"], caption, artifacts["captioned"])
    report("probing outputs")
    probes = {name: probe(path) for name, path in artifacts.items()}
    report("building contact sheet")
    contact_sheet = generate_contact_sheet(artifacts, output_dir)
    report("complete")
    return artifacts, probes, contact_sheet


def render(state: PrototypeState, plan: SourceSignaturePlan) -> None:
    print("\033[2J\033[H", end="")
    print("\033[1mFrameCredit — PROTOTYPE: Source Signature\033[0m")
    print("\033[2mQuestion: does attribution remain visible after ordinary transformations?\033[0m\n")
    print(f"\033[1mstatus\033[0m: {state.status}")
    print(f"\033[1moutput\033[0m: {state.output_dir or 'temporary directory created on generation'}")
    print(f"\033[1mselected\033[0m: {state.selected_name}")
    if state.selected_name in state.probes:
        print(f"\033[1mprobe\033[0m: {json.dumps(state.probes[state.selected_name], ensure_ascii=False)}")
    print("\n\033[1mMarker schedule\033[0m")
    for window in plan.marker_windows:
        print(f"  {window.start:>4.1f}s–{window.end:>4.1f}s  {window.position}")
    print("\n\033[1mSource Card schedule\033[0m")
    for window in plan.card_windows:
        print(f"  {window.start:>4.1f}s–{window.end:>4.1f}s")
    print("\n\033[1mControls\033[0m")
    print("  [g] generate  [n] next rendition  [o] open rendition  [c] contact sheet  [q] quit")


def open_path(path: Path) -> None:
    opener = shutil.which("open")
    if opener is None:
        raise RuntimeError(f"open manually: {path}")
    subprocess.Popen([opener, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def interactive() -> int:
    plan = build_plan(DURATION)
    state = PrototypeState()
    with tempfile.TemporaryDirectory(prefix="framecredit-prototype-") as temp:
        output_dir = Path(temp)
        while True:
            render(state, plan)
            command = input("\n> ").strip().lower()
            if command == "q":
                return 0
            if command == "n":
                state.selected_index = (state.selected_index + 1) % len(VARIANT_ORDER)
                continue
            if command == "g":
                if state.artifacts:
                    state.status = "already generated"
                    continue

                def progress(message: str) -> None:
                    state.status = message
                    state.output_dir = output_dir
                    render(state, plan)

                try:
                    artifacts, probes, contact_sheet = generate_artifacts(output_dir, plan, progress)
                    state.artifacts = artifacts
                    state.probes = probes
                    state.contact_sheet = contact_sheet
                    state.status = "complete"
                except Exception as exc:  # throwaway shell surfaces the full experiment error
                    state.status = f"failed: {exc}"
                continue
            if command == "o":
                path = state.artifacts.get(state.selected_name)
                state.status = "generate first" if path is None else f"opened {path.name}"
                if path:
                    open_path(path)
                continue
            if command == "c":
                state.status = "generate first" if state.contact_sheet is None else "opened contact sheet"
                if state.contact_sheet:
                    open_path(state.contact_sheet)
                continue
            state.status = f"unknown command: {command or '<empty>'}"


def batch(output_dir: Path | None) -> int:
    plan = build_plan(DURATION)
    destination = output_dir or Path(tempfile.mkdtemp(prefix="framecredit-prototype-"))
    artifacts, probes, contact_sheet = generate_artifacts(
        destination,
        plan,
        progress=lambda message: print(f"[prototype] {message}"),
    )
    print(
        json.dumps(
            {
                "question": "Does the Source Signature remain visible after ordinary transformations?",
                "output_dir": str(destination),
                "artifacts": {name: str(path) for name, path in artifacts.items()},
                "contact_sheet": str(contact_sheet),
                "probes": probes,
                "plan": plan.as_dict(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true", help="generate artifacts without the TUI")
    parser.add_argument("--output", type=Path, help="empty output directory for --generate")
    args = parser.parse_args()
    if args.output is not None and not args.generate:
        parser.error("--output requires --generate")
    return batch(args.output) if args.generate else interactive()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nprototype interrupted")
        raise SystemExit(130)
    except Exception as exc:
        print(f"prototype failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
