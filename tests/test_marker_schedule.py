import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FFMPEG = shutil.which("ffmpeg")


@unittest.skipUnless(FFMPEG, "ffmpeg is required")
class CreatorMarkerScheduleTest(unittest.TestCase):
    def test_long_creator_identity_respects_small_video_width(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-marker-test-") as temp_dir:
            workdir = Path(temp_dir)
            source = workdir / "small-source.mp4"
            output = workdir / "attributed.mp4"
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
                    "color=c=gray:s=240x160:r=24",
                    "-t",
                    "2",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-pix_fmt",
                    "yuv420p",
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
                    "--creator-name",
                    "Shen Sean Chen",
                    "--x-handle",
                    "@ShenSeanChen",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            frame = self._extract_frame(output, 1, workdir)
            with Image.open(frame).convert("L") as image:
                dark_panel = image.point(lambda value: 255 if value < 80 else 0).getbbox()
                bright_text = image.point(lambda value: 255 if value > 200 else 0).getbbox()
            self.assertIsNotNone(dark_panel)
            self.assertIsNotNone(bright_text)
            assert dark_panel is not None and bright_text is not None
            self.assertLessEqual(dark_panel[2] - dark_panel[0], 240 * 0.35)
            self.assertGreater(bright_text[0], dark_panel[0])
            self.assertGreater(bright_text[1], dark_panel[1])
            self.assertLess(bright_text[2], dark_panel[2])
            self.assertLess(bright_text[3], dark_panel[3])

    def test_creator_marker_remains_readable_on_light_background(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-marker-test-") as temp_dir:
            workdir = Path(temp_dir)
            source = workdir / "light-source.mp4"
            output = workdir / "attributed.mp4"
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
                    "color=c=white:s=480x270:r=24",
                    "-t",
                    "2",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-pix_fmt",
                    "yuv420p",
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
                    "--creator-name",
                    "小明",
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

            frame = self._extract_frame(output, 1, workdir)
            with Image.open(frame).convert("L") as image:
                marker_region = image.crop((0, 0, 250, 100))
                darkest, brightest = marker_region.getextrema()
            self.assertLess(darkest, 64, "Creator Marker needs a dark contrast panel")
            self.assertGreater(brightest, 220, "Creator Identity needs bright readable text")

    def test_long_creator_identity_stays_compact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-marker-test-") as temp_dir:
            workdir = Path(temp_dir)
            source = workdir / "source.mp4"
            output = workdir / "attributed.mp4"
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
                    "color=c=black:s=1280x720:r=24",
                    "-t",
                    "2",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-pix_fmt",
                    "yuv420p",
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
                    "--creator-name",
                    "Shen Sean Chen",
                    "--x-handle",
                    "@ShenSeanChen",
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            left, top, right, bottom = self._visible_content_box(output, 1, workdir)
            self.assertLessEqual(
                right - left,
                1280 * 0.35,
                "a long Creator Identity should not become a full-width banner",
            )
            self.assertLessEqual(bottom - top, 720 * 0.12)

    def test_creator_marker_uses_three_safe_positions_over_time(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-schedule-test-") as temp_dir:
            workdir = Path(temp_dir)
            source = workdir / "source.mp4"
            output = workdir / "attributed.mp4"
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
                    "color=c=black:s=480x270:r=24",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:sample_rate=48000",
                    "-t",
                    "38",
                    "-shortest",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
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
                    "--creator-name",
                    "小明",
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

            timestamps = (3, 11, 13, 23, 25, 35)
            boxes = [
                self._visible_content_box(output, timestamp, workdir)
                for timestamp in timestamps
            ]
            centers = [((left + right) / 2, (top + bottom) / 2) for left, top, right, bottom in boxes]

            self.assertLess(centers[0][0], 480 * 0.4, "first position should be top-left")
            self.assertLess(centers[1][0], 480 * 0.4, "position should remain top-left before 12s")
            self.assertGreater(centers[2][0], 480 * 0.6, "position should switch to top-right after 12s")
            self.assertGreater(centers[3][0], 480 * 0.6, "position should remain top-right before 24s")
            self.assertGreater(centers[4][0], 480 * 0.4, "position should switch to centered after 24s")
            self.assertLess(centers[4][0], 480 * 0.6, "position should switch to centered after 24s")
            self.assertGreater(centers[5][0], 480 * 0.4, "position should remain centered before 36s")
            self.assertLess(centers[5][0], 480 * 0.6, "position should remain centered before 36s")
            self.assertTrue(
                all(bottom < 270 * 0.75 for _, _, _, bottom in boxes),
                "the Creator Marker should stay above the subtitle region",
            )

            repeated_output = workdir / "attributed-repeat.mp4"
            repeated_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "framecredit",
                    "process",
                    str(source),
                    "--creator-name",
                    "小明",
                    "--x-handle",
                    "@xiaoming",
                    "--output",
                    str(repeated_output),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
            )
            self.assertEqual(repeated_result.returncode, 0, repeated_result.stderr)
            repeated_boxes = [
                self._visible_content_box(repeated_output, timestamp, workdir)
                for timestamp in (3, 15, 27)
            ]
            self.assertEqual(repeated_boxes, [boxes[0], boxes[2], boxes[4]])

    def _visible_content_box(
        self,
        video: Path,
        timestamp: int,
        workdir: Path,
    ) -> tuple[int, int, int, int]:
        frame = self._extract_frame(video, timestamp, workdir)
        with Image.open(frame).convert("L") as image:
            visible = image.point(lambda value: 255 if value > 96 else 0)
            box = visible.getbbox()
        self.assertIsNotNone(box, f"Creator Marker should be visible at {timestamp}s")
        assert box is not None
        return box

    def _extract_frame(self, video: Path, timestamp: int, workdir: Path) -> Path:
        frame = workdir / f"frame-{timestamp}.png"
        subprocess.run(
            [
                FFMPEG,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-ss",
                str(timestamp),
                "-i",
                str(video),
                "-frames:v",
                "1",
                str(frame),
            ],
            check=True,
        )
        return frame


if __name__ == "__main__":
    unittest.main()
