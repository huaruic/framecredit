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
sys.path.insert(0, str(ROOT / "src"))

from framecredit.processing import normalize_x_handle

FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")


class CreatorIdentityNormalizationTest(unittest.TestCase):
    def test_a_bare_handle_is_stored_with_a_leading_at_sign(self) -> None:
        self.assertEqual(normalize_x_handle("xiaoming"), "@xiaoming")
        self.assertEqual(normalize_x_handle(" @xiaoming "), "@xiaoming")


@unittest.skipUnless(FFMPEG and FFPROBE, "ffmpeg and ffprobe are required")
class ProcessCommandTest(unittest.TestCase):
    def _cli_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        return env

    def _create_source_video(self, path: Path) -> None:
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
                "color=c=black:s=320x180:r=24",
                "-t",
                "1",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(path),
            ],
            check=True,
        )

    def _run_process(self, source: Path, output: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
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
            env=self._cli_env(),
            capture_output=True,
            text=True,
        )

    def test_process_command_reports_an_unreadable_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-test-") as temp_dir:
            workdir = Path(temp_dir)
            garbage = workdir / "broken.mp4"
            garbage.write_bytes(b"this is not a video")
            output = workdir / "attributed.mp4"

            result = self._run_process(garbage, output)

            self.assertEqual(result.returncode, 1)
            self.assertIn("could not read the source video", result.stderr)
            self.assertFalse(output.exists())

    def test_process_command_rejects_a_still_image_source(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-test-") as temp_dir:
            workdir = Path(temp_dir)
            still = workdir / "picture.png"
            Image.new("RGB", (320, 240), (24, 24, 24)).save(still)
            output = workdir / "attributed.mp4"

            result = self._run_process(still, output)

            self.assertEqual(result.returncode, 1)
            self.assertIn("not a playable video", result.stderr)
            self.assertFalse(output.exists())

    def test_process_command_does_not_overwrite_an_existing_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-test-") as temp_dir:
            workdir = Path(temp_dir)
            source = workdir / "source.mp4"
            self._create_source_video(source)
            output = workdir / "attributed.mp4"
            output.write_bytes(b"existing export")

            result = self._run_process(source, output)

            self.assertEqual(result.returncode, 1)
            self.assertIn("already exists", result.stderr)
            self.assertEqual(output.read_bytes(), b"existing export")

    @unittest.skipIf(os.name == "nt", "read-only directory permissions are POSIX-only")
    def test_a_failed_export_leaves_no_partial_output(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-test-") as temp_dir:
            workdir = Path(temp_dir)
            source = workdir / "source.mp4"
            self._create_source_video(source)
            locked = workdir / "locked"
            locked.mkdir()
            os.chmod(locked, 0o500)
            try:
                result = self._run_process(source, locked / "attributed.mp4")

                self.assertEqual(result.returncode, 1)
                self.assertIn("could not create the Attributed Export", result.stderr)
                self.assertEqual(list(locked.iterdir()), [])
            finally:
                os.chmod(locked, 0o700)

    def test_version_flag_reports_the_installed_version(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "framecredit", "--version"],
            cwd=ROOT,
            env=self._cli_env(),
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertRegex(result.stdout, r"^framecredit \S+")

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

            bare_handle_output = workdir / "bare-handle.mp4"
            bare_handle_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "framecredit",
                    "process",
                    str(source),
                    "--x-handle",
                    "xiaoming",
                    "--output",
                    str(bare_handle_output),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(bare_handle_result.returncode, 0, bare_handle_result.stderr)

            bare_handle_frame = workdir / "bare-handle.png"
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
                    str(bare_handle_output),
                    "-frames:v",
                    "1",
                    str(bare_handle_frame),
                ],
                check=True,
            )
            with (
                Image.open(frame).convert("RGB") as with_at_sign,
                Image.open(bare_handle_frame).convert("RGB") as without_at_sign,
            ):
                self.assertIsNone(
                    ImageChops.difference(with_at_sign, without_at_sign).getbbox(),
                    "a handle entered without @ should render the same "
                    "X · @handle Creator Marker as the @-prefixed form",
                )


if __name__ == "__main__":
    unittest.main()
