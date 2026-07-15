from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "site" / "index.html"


class LandingPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = LANDING.read_text(encoding="utf-8")

    def test_every_command_block_has_copy_control_and_status(self) -> None:
        command_blocks = re.findall(
            r'class="[^"]*\bcommand-block\b[^"]*"', self.html
        )
        copy_buttons = re.findall(r"<button[^>]+\bdata-copy\b", self.html)
        copy_statuses = re.findall(r"data-copy-status[^>]+aria-live=\"polite\"", self.html)

        self.assertGreater(len(command_blocks), 0)
        self.assertEqual(len(command_blocks), len(copy_buttons))
        self.assertEqual(len(command_blocks), len(copy_statuses))
        self.assertIn("navigator.clipboard?.writeText", self.html)

    def test_cli_export_command_is_not_inline_body_copy(self) -> None:
        command = (
            'framecredit process input.mp4 --x-handle "@yourhandle" '
            "--output attributed.mp4"
        )
        self.assertIn(f"<pre><code>{command}</code></pre>", self.html)

        paragraphs = re.findall(r"<p\b[^>]*>.*?</p>", self.html, re.DOTALL)
        self.assertTrue(all(command not in paragraph for paragraph in paragraphs))


if __name__ == "__main__":
    unittest.main()
