from dataclasses import dataclass
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont


MARKER_INTERVAL_SECONDS = 12


@dataclass(frozen=True)
class ProcessRequest:
    source: Path
    output: Path
    creator_name: str
    x_handle: str


class ProcessingError(RuntimeError):
    """A user-facing media processing failure."""


def create_attributed_export(request: ProcessRequest) -> Path:
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
            creator_name=request.creator_name,
            x_handle=request.x_handle,
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
    creator_name: str,
    x_handle: str,
    video_width: int,
    video_height: int,
    margin: int,
) -> None:
    single_line = f"原创：{creator_name}  {x_handle}"
    lines = (single_line,)
    base_font_size = max(16, round(video_height * 0.045))
    minimum_font_size = max(6, round(video_height * 0.015))
    font_size = base_font_size
    font_path = _find_font()
    available_width = video_width - (margin * 2)
    max_width = max(1, min(available_width, int(video_width * 0.35)))
    probe = Image.new("RGBA", (1, 1))
    probe_draw = ImageDraw.Draw(probe)

    while True:
        font = ImageFont.truetype(font_path, font_size)
        padding_x = max(3, round(font_size * 0.65))
        spacing = max(2, round(font_size * 0.18))
        text = "\n".join(lines)
        bounds = probe_draw.multiline_textbbox(
            (0, 0),
            text,
            font=font,
            spacing=spacing,
        )
        text_width = bounds[2] - bounds[0]
        if text_width + (padding_x * 2) <= max_width:
            break
        if lines == (single_line,):
            lines = (f"原创：{creator_name}", x_handle)
            font_size = base_font_size
            continue
        if font_size <= minimum_font_size:
            text_width_limit = max(1, max_width - (padding_x * 2))
            lines = tuple(
                _ellipsize_text(probe_draw, line, font, text_width_limit)
                for line in lines
            )
            text = "\n".join(lines)
            bounds = probe_draw.multiline_textbbox(
                (0, 0),
                text,
                font=font,
                spacing=spacing,
            )
            text_width = bounds[2] - bounds[0]
            break
        font_size -= 1

    padding_y = max(3, round(font_size * 0.4))
    marker_width = text_width + (padding_x * 2)
    marker_height = (bounds[3] - bounds[1]) + (padding_y * 2)
    radius = max(6, round(marker_height * 0.22))

    image = Image.new("RGBA", (marker_width, marker_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (0, 0, marker_width - 1, marker_height - 1),
        radius=radius,
        fill=(10, 15, 24, 218),
        outline=(255, 255, 255, 70),
        width=1,
    )
    draw.multiline_text(
        (padding_x - bounds[0], padding_y - bounds[1]),
        text,
        font=font,
        spacing=spacing,
        fill=(255, 255, 255, 255),
    )
    image.save(output)


def _ellipsize_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
) -> str:
    def rendered_width(value: str) -> int:
        bounds = draw.textbbox((0, 0), value, font=font)
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
    phase = f"mod(floor(t/{MARKER_INTERVAL_SECONDS}),3)"
    x_position = (
        f"if(eq({phase},0),{margin},"
        f"if(eq({phase},1),W-w-{margin},(W-w)/2))"
    )
    y_position = f"if(eq({phase},2),H*0.18,{margin})"
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
