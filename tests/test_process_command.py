import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")


@unittest.skipUnless(FFMPEG and FFPROBE, "ffmpeg and ffprobe are required")
class ProcessCommandTest(unittest.TestCase):
    def test_process_command_requires_only_the_x_handle_for_creator_identity(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")

        result = subprocess.run(
            [sys.executable, "-m", "framecredit", "process", "--help"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--x-handle", result.stdout)
        self.assertNotIn("--creator-name", result.stdout)

    def test_process_command_rejects_a_non_searchable_x_handle(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-test-") as temp_dir:
            workdir = Path(temp_dir)
            output = workdir / "attributed.mp4"
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT / "src")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "framecredit",
                    "process",
                    str(workdir / "missing.mp4"),
                    "--x-handle",
                    "not a handle",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn("valid X handle", result.stderr)
            self.assertFalse(output.exists())

    def test_creator_can_generate_a_playable_attributed_export(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-test-") as temp_dir:
            workdir = Path(temp_dir)
            source = workdir / "source.mp4"
            output = workdir / "attributed.mp4"
            frame = workdir / "frame.png"

            subprocess.run(
                [
                    FFMPEG,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    "color=c=black:s=640x360:r=24",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:sample_rate=48000",
                    "-t",
                    "2",
                    "-shortest",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "aac",
                    str(source),
                ],
                check=True,
            )

            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT / "src")
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "framecredit",
                    "process",
                    str(source),
                    "--x-handle",
                    "@xiaoming",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output.is_file())
            self.assertIn(str(output), result.stdout)

            probe = subprocess.run(
                [
                    FFPROBE,
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration:stream=codec_type,width,height,start_time,duration",
                    "-of",
                    "json",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            media = json.loads(probe.stdout)
            video_stream = next(
                stream
                for stream in media["streams"]
                if stream["codec_type"] == "video"
            )
            self.assertEqual((video_stream["width"], video_stream["height"]), (640, 360))
            self.assertTrue(
                any(stream["codec_type"] == "audio" for stream in media["streams"])
            )
            self.assertAlmostEqual(float(media["format"]["duration"]), 2.0, delta=0.15)
            audio_stream = next(
                stream
                for stream in media["streams"]
                if stream["codec_type"] == "audio"
            )
            video_start = float(video_stream["start_time"])
            audio_start = float(audio_stream["start_time"])
            video_end = video_start + float(video_stream["duration"])
            audio_end = audio_start + float(audio_stream["duration"])
            self.assertAlmostEqual(audio_start, video_start, delta=1 / 24)
            self.assertAlmostEqual(audio_end, video_end, delta=0.15)

            misleading_suffix = workdir / "still-an-mp4.mov"
            suffix_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "framecredit",
                    "process",
                    str(source),
                    "--x-handle",
                    "@xiaoming",
                    "--output",
                    str(misleading_suffix),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(suffix_result.returncode, 0, suffix_result.stderr)
            suffix_probe = subprocess.run(
                [
                    FFPROBE,
                    "-v",
                    "error",
                    "-show_entries",
                    "format_tags=major_brand",
                    "-of",
                    "json",
                    str(misleading_suffix),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            suffix_media = json.loads(suffix_probe.stdout)
            self.assertEqual(suffix_media["format"]["tags"]["major_brand"], "isom")

            different_handle = workdir / "different-handle.mp4"
            handle_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "framecredit",
                    "process",
                    str(source),
                    "--x-handle",
                    "@another",
                    "--output",
                    str(different_handle),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(handle_result.returncode, 0, handle_result.stderr)

            subprocess.run(
                [
                    FFMPEG,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-ss",
                    "1",
                    "-i",
                    str(output),
                    "-frames:v",
                    "1",
                    str(frame),
                ],
                check=True,
            )
            with Image.open(frame).convert("RGB") as rendered:
                marker_area = rendered.crop((0, 0, 420, 100))
                brightest_channel = max(
                    channel_max for _, channel_max in marker_area.getextrema()
                )
            self.assertGreater(
                brightest_channel,
                200,
                "the exported frame should visibly contain the creator marker",
            )

            handle_frame = workdir / "different-handle.png"
            subprocess.run(
                [
                    FFMPEG,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-ss",
                    "1",
                    "-i",
                    str(different_handle),
                    "-frames:v",
                    "1",
                    str(handle_frame),
                ],
                check=True,
            )

            with (
                Image.open(frame).convert("RGB") as original_identity,
                Image.open(handle_frame).convert("RGB") as changed_handle,
            ):
                original_marker = original_identity.crop((0, 0, 420, 100))
                handle_marker = changed_handle.crop((0, 0, 420, 100))
                self.assertIsNotNone(
                    ImageChops.difference(original_marker, handle_marker).getbbox(),
                    "changing the X handle should change the visible marker",
                )


if __name__ == "__main__":
    unittest.main()
