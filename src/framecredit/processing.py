from dataclasses import dataclass
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont


MARKER_INTERVAL_SECONDS = 30
X_HANDLE_PATTERN = re.compile(r"@?([A-Za-z0-9_]{1,15})\Z")


@dataclass(frozen=True)
class ProcessRequest:
    source: Path
    output: Path
    x_handle: str


class ProcessingError(RuntimeError):
    """A user-facing media processing failure."""


def create_attributed_export(request: ProcessRequest) -> Path:
    x_handle = normalize_x_handle(request.x_handle)
    ffmpeg = _required_command("ffmpeg")
    ffprobe = _required_command("ffprobe")

    if not request.source.is_file():
        raise ProcessingError(f"source video does not exist: {request.source}")

    width, height = _video_dimensions(ffprobe, request.source)
    request.output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="framecredit-") as temp_dir:
        marker_path = Path(temp_dir) / "creator-marker.png"
        margin = max(10, round(height * 0.03))
        _render_creator_marker(
            marker_path,
            x_handle=x_handle,
            video_width=width,
            video_height=height,
            margin=margin,
        )
        _burn_marker(
            ffmpeg=ffmpeg,
            source=request.source,
            marker=marker_path,
            output=request.output,
            margin=margin,
        )

    return request.output.resolve()


def normalize_x_handle(value: str) -> str:
    match = X_HANDLE_PATTERN.fullmatch(value.strip())
    if match is None:
        raise ProcessingError(
            "enter a valid X handle using 1–15 letters, numbers, or underscores"
        )
    return f"@{match.group(1)}"


def _required_command(name: str) -> str:
    command = shutil.which(name)
    if command is None:
        raise ProcessingError(f"{name} is required but was not found on PATH")
    return command


def _video_dimensions(ffprobe: str, source: Path) -> tuple[int, int]:
    command = [
        ffprobe,
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "json",
        str(source),
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        stream = json.loads(result.stdout)["streams"][0]
        return int(stream["width"]), int(stream["height"])
    except (subprocess.CalledProcessError, KeyError, IndexError, ValueError, json.JSONDecodeError) as error:
        raise ProcessingError(f"could not read the source video: {source}") from error


def _render_creator_marker(
    output: Path,
    *,
    x_handle: str,
    video_width: int,
    video_height: int,
    margin: int,
) -> None:
    text = f"X · {x_handle}"
    base_font_size = max(12, round(video_height * 0.034))
    minimum_font_size = max(6, round(video_height * 0.018))
    font_size = base_font_size
    font_path = _find_font()
    available_width = video_width - (margin * 2)
    width_ratio = 0.35 if video_width < 480 else 0.20
    max_width = max(1, min(available_width, int(video_width * width_ratio)))
    probe = Image.new("RGBA", (1, 1))
    probe_draw = ImageDraw.Draw(probe)

    while True:
        font = ImageFont.truetype(font_path, font_size)
        stroke_width = max(1, round(font_size * 0.09))
        padding = stroke_width + 1
        bounds = probe_draw.textbbox(
            (0, 0), text, font=font, stroke_width=stroke_width
        )
        text_width = bounds[2] - bounds[0]
        if text_width + (padding * 2) <= max_width:
            break
        if font_size <= minimum_font_size:
            text = _ellipsize_text(
                probe_draw,
                text,
                font,
                max(1, max_width - (padding * 2)),
                stroke_width=stroke_width,
            )
            bounds = probe_draw.textbbox(
                (0, 0), text, font=font, stroke_width=stroke_width
            )
            text_width = bounds[2] - bounds[0]
            break
        font_size -= 1

    marker_width = text_width + (padding * 2)
    marker_height = (bounds[3] - bounds[1]) + (padding * 2)

    image = Image.new("RGBA", (marker_width, marker_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text(
        (padding - bounds[0], padding - bounds[1]),
        text,
        font=font,
        fill=(255, 255, 255, 220),
        stroke_width=stroke_width,
        stroke_fill=(0, 0, 0, 220),
    )
    image.save(output)


def _ellipsize_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    *,
    stroke_width: int = 0,
) -> str:
    def rendered_width(value: str) -> int:
        bounds = draw.textbbox(
            (0, 0), value, font=font, stroke_width=stroke_width
        )
        return bounds[2] - bounds[0]

    if rendered_width(text) <= max_width:
        return text
    ellipsis = "…"
    if rendered_width(ellipsis) > max_width:
        return ""
    candidate = text
    while candidate and rendered_width(candidate + ellipsis) > max_width:
        candidate = candidate[:-1]
    return candidate + ellipsis


def _find_font() -> str:
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    raise ProcessingError("no supported font was found for the Creator Marker")


def _burn_marker(
    *,
    ffmpeg: str,
    source: Path,
    marker: Path,
    output: Path,
    margin: int,
) -> None:
    phase = f"mod(floor(t/{MARKER_INTERVAL_SECONDS}),2)"
    x_position = f"if(eq({phase},0),{margin},W-w-{margin})"
    y_position = str(margin)
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source),
        "-loop",
        "1",
        "-framerate",
        "30",
        "-i",
        str(marker),
        "-filter_complex",
        "[0:v][1:v]overlay="
        f"x='{x_position}':y='{y_position}':eval=frame:shortest=1[v]",
        "-map",
        "[v]",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-movflags",
        "+faststart",
        "-shortest",
        "-f",
        "mp4",
        str(output),
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip().splitlines()
        message = detail[-1] if detail else "unknown ffmpeg error"
        raise ProcessingError(f"could not create the Attributed Export: {message}") from error
