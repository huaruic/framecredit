import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
FFMPEG = shutil.which("ffmpeg")
PLAYWRIGHT_CLI = shutil.which("playwright-cli")


class LocalAppTest(unittest.TestCase):
    @unittest.skipUnless(FFMPEG and PLAYWRIGHT_CLI, "ffmpeg and playwright-cli are required")
    def test_browser_workflow_reports_progress_and_result(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-browser-test-") as temp_dir:
            workdir = Path(temp_dir)
            source = workdir / "lesson.mp4"
            output_dir = workdir / "exports"
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
                    "testsrc2=size=1280x720:rate=30",
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=440:sample_rate=48000",
                    "-t",
                    "6",
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
            env["FRAMECREDIT_HOME"] = str(workdir / "app-data")
            env["FRAMECREDIT_OUTPUT_DIR"] = str(output_dir)
            app, url = self._start_app(env)
            session = f"framecredit-{os.getpid()}"
            script = f"""async page => {{
                await page.locator('#x-handle').fill('@xiaoming');
                const marker = await page.locator('#identity-preview').textContent();
                if (marker !== 'X · @xiaoming') throw new Error(`wrong marker preview: ${{marker}}`);
                await page.locator('#source-video').setInputFiles({json.dumps(str(source))});
                await page.locator('#preview-canvas').waitFor({{state: 'visible', timeout: 10000}});
                const positionNote = await page.locator('#preview-controls').textContent();
                if (!positionNote.includes('Preview only · export alternates automatically every 30 seconds')) {{
                    throw new Error(`missing preview-only note: ${{positionNote}}`);
                }}
                await page.locator('#process-video').click();
                await page.waitForTimeout(500);
                const progress = await page.locator('#progress').textContent();
                if (!progress.includes('elapsed')) throw new Error(`missing elapsed progress: ${{progress}}`);
                await page.locator('#result.visible').waitFor({{state: 'visible', timeout: 30000}});
                const output = await page.locator('#result-path').textContent();
                if (!output.endsWith('lesson-attributed.mp4')) throw new Error(`wrong result: ${{output}}`);
                return output;
            }}"""
            try:
                browser_open = subprocess.run(
                    [PLAYWRIGHT_CLI, f"-s={session}", "open", url],
                    capture_output=True,
                    text=True,
                )
                if browser_open.returncode != 0:
                    detail = (browser_open.stdout + browser_open.stderr).strip()
                    if os.environ.get("CI") or os.environ.get(
                        "FRAMECREDIT_REQUIRE_PLAYWRIGHT"
                    ) == "1":
                        self.fail(f"playwright-cli could not start: {detail}")
                    self.skipTest(f"playwright-cli could not start: {detail}")
                browser_result = subprocess.run(
                    [PLAYWRIGHT_CLI, f"-s={session}", "run-code", script],
                    capture_output=True,
                    text=True,
                )
                browser_output = browser_result.stdout + browser_result.stderr
                self.assertEqual(
                    browser_result.returncode,
                    0,
                    browser_output,
                )
                self.assertNotIn("### Error", browser_output, browser_output)
                self.assertIn("lesson-attributed.mp4", browser_output)
            finally:
                subprocess.run(
                    [PLAYWRIGHT_CLI, f"-s={session}", "close"],
                    capture_output=True,
                    text=True,
                )
                self._stop_app(app)

            self.assertTrue((output_dir / "lesson-attributed.mp4").is_file())

    def test_local_interface_presents_the_complete_creator_workflow(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-app-test-") as temp_dir:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT / "src")
            env["FRAMECREDIT_HOME"] = str(Path(temp_dir) / "app-data")
            app, url = self._start_app(env)
            try:
                with urlopen(url, timeout=5) as response:
                    page = response.read().decode("utf-8")
            finally:
                self._stop_app(app)

            self.assertIn('lang="en"', page)
            self.assertNotIn('id="creator-name"', page)
            self.assertIn('id="x-handle"', page)
            self.assertIn('id="identity-preview"', page)
            self.assertIn('X · @handle', page)
            self.assertIn('id="drop-zone"', page)
            self.assertIn('id="source-video"', page)
            self.assertIn(
                'Preview only · export alternates automatically every 30 seconds',
                page,
            )
            self.assertIn('id="progress"', page)
            self.assertIn('id="result-path"', page)
            self.assertIn('id="open-output"', page)

    def test_creator_identity_is_retained_for_later_sessions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-app-test-") as temp_dir:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT / "src")
            env["FRAMECREDIT_HOME"] = str(Path(temp_dir) / "app-data")

            first_app, first_url = self._start_app(env)
            try:
                initial = self._json_request(f"{first_url}/api/identity")
                self.assertEqual(initial, {"x_handle": ""})

                saved = self._json_request(
                    f"{first_url}/api/identity",
                    method="PUT",
                    body={"x_handle": "@xiaoming"},
                )
                self.assertEqual(saved, {"x_handle": "@xiaoming"})
            finally:
                self._stop_app(first_app)

            second_app, second_url = self._start_app(env)
            try:
                retained = self._json_request(f"{second_url}/api/identity")
                self.assertEqual(retained, {"x_handle": "@xiaoming"})
            finally:
                self._stop_app(second_app)

    def test_saved_handle_survives_the_previous_identity_file_shape(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-app-test-") as temp_dir:
            app_home = Path(temp_dir) / "app-data"
            app_home.mkdir(parents=True)
            (app_home / "identity.json").write_text(
                json.dumps(
                    {"creator_name": "Previous Name", "x_handle": "@xiaoming"}
                ),
                encoding="utf-8",
            )
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT / "src")
            env["FRAMECREDIT_HOME"] = str(app_home)

            app, url = self._start_app(env)
            try:
                retained = self._json_request(f"{url}/api/identity")
                self.assertEqual(retained, {"x_handle": "@xiaoming"})
            finally:
                self._stop_app(app)

    def test_local_interface_rejects_a_non_searchable_x_handle(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-app-test-") as temp_dir:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT / "src")
            env["FRAMECREDIT_HOME"] = str(Path(temp_dir) / "app-data")

            app, url = self._start_app(env)
            try:
                with self.assertRaises(HTTPError) as captured:
                    self._json_request(
                        f"{url}/api/identity",
                        method="PUT",
                        body={"x_handle": "not a handle"},
                    )
                payload = json.loads(captured.exception.read().decode("utf-8"))
                captured.exception.close()
                self.assertIn("valid X handle", payload["error"])
            finally:
                self._stop_app(app)

    @unittest.skipUnless(FFMPEG, "ffmpeg is required")
    def test_local_interface_processes_source_and_reports_result(self) -> None:
        with tempfile.TemporaryDirectory(prefix="framecredit-app-test-") as temp_dir:
            workdir = Path(temp_dir)
            source = workdir / "lesson.mp4"
            output_dir = workdir / "exports"
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
                    "1",
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
            env["FRAMECREDIT_HOME"] = str(workdir / "app-data")
            env["FRAMECREDIT_OUTPUT_DIR"] = str(output_dir)
            app, url = self._start_app(env)
            try:
                self._json_request(
                    f"{url}/api/identity",
                    method="PUT",
                    body={"x_handle": "@xiaoming"},
                )
                request = Request(
                    f"{url}/api/process",
                    data=source.read_bytes(),
                    method="POST",
                    headers={
                        "Content-Type": "video/mp4",
                        "X-FrameCredit-Filename": source.name,
                    },
                )
                with urlopen(request, timeout=15) as response:
                    result = json.loads(response.read().decode("utf-8"))

                second_request = Request(
                    f"{url}/api/process",
                    data=source.read_bytes(),
                    method="POST",
                    headers={
                        "Content-Type": "video/mp4",
                        "X-FrameCredit-Filename": source.name,
                    },
                )
                with urlopen(second_request, timeout=15) as response:
                    second_result = json.loads(response.read().decode("utf-8"))
            finally:
                self._stop_app(app)

            output = Path(result["output"])
            self.assertTrue(output.is_file())
            self.assertEqual(output.parent, output_dir.resolve())
            self.assertEqual(output.name, "lesson-attributed.mp4")
            self.assertEqual(result["open_url"], "/api/open/lesson-attributed.mp4")
            second_output = Path(second_result["output"])
            self.assertTrue(second_output.is_file())
            self.assertEqual(second_output.name, "lesson-attributed-2.mp4")
            self.assertNotEqual(second_output, output)

    def _start_app(self, env: dict[str, str]) -> tuple[subprocess.Popen[str], str]:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "framecredit",
                "app",
                "--port",
                "0",
                "--no-browser",
            ],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        startup_line = process.stdout.readline().strip()
        if not startup_line.startswith("FrameCredit local app: "):
            assert process.stderr is not None
            error = process.stderr.read()
            process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()
            self.fail(f"local app did not start: {startup_line}\n{error}")
        return process, startup_line.removeprefix("FrameCredit local app: ")

    def _stop_app(self, process: subprocess.Popen[str]) -> None:
        process.terminate()
        process.wait(timeout=5)
        if process.stdout is not None:
            process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()

    def _json_request(
        self,
        url: str,
        *,
        method: str = "GET",
        body: dict[str, str] | None = None,
    ) -> dict[str, str]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = Request(
            url,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
