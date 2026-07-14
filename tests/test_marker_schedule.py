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
    def test_x_handle_marker_respects_small_video_width(self) -> None:
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
                    "color=c=black:s=240x160:r=24",
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
            self.assertLessEqual(right - left, 240 * 0.32)
            self.assertLessEqual(bottom - top, 160 * 0.08)
            self.assertGreaterEqual(left, 0)
            self.assertGreaterEqual(top, 0)
            self.assertLessEqual(right, 240)
            self.assertLessEqual(bottom, 160)

    def test_creator_marker_uses_outline_instead_of_an_opaque_panel(self) -> None:
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
                dark_pixels = sum(
                    value < 64 for value in marker_region.get_flattened_data()
                )
                dark_ratio = dark_pixels / (marker_region.width * marker_region.height)
            self.assertGreater(dark_pixels, 20, "the light marker needs a dark outline")
            self.assertLess(
                dark_ratio,
                0.02,
                "the Creator Marker must not contain a large opaque panel",
            )

    def test_x_handle_marker_stays_compact(self) -> None:
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
                1280 * 0.20,
                "the X handle marker should remain narrow",
            )
            self.assertLessEqual(
                bottom - top,
                720 * 0.06,
                "the X handle marker should remain one compact line",
            )

    def test_creator_marker_alternates_between_top_corners_every_thirty_seconds(self) -> None:
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
                    "64",
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

            timestamps = (3, 29, 31, 59, 61)
            boxes = [
                self._visible_content_box(output, timestamp, workdir)
                for timestamp in timestamps
            ]
            centers = [((left + right) / 2, (top + bottom) / 2) for left, top, right, bottom in boxes]

            self.assertLess(centers[0][0], 480 * 0.4, "first position should be top-left")
            self.assertLess(centers[1][0], 480 * 0.4, "position should remain top-left before 30s")
            self.assertGreater(centers[2][0], 480 * 0.6, "position should switch to top-right after 30s")
            self.assertGreater(centers[3][0], 480 * 0.6, "position should remain top-right before 60s")
            self.assertLess(centers[4][0], 480 * 0.4, "position should return to top-left after 60s")
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
                for timestamp in (3, 31, 61)
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
