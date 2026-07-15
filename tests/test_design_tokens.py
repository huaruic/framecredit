from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]

LANDING = ROOT / "site" / "index.html"
APP = ROOT / "src" / "framecredit" / "static" / "index.html"

BLOCK = re.compile(
    r"/\* GEIST TOKENS v\d+.*?/\* END GEIST TOKENS v\d+ \*/", re.DOTALL
)


def _token_block(page: Path) -> str:
    match = BLOCK.search(page.read_text(encoding="utf-8"))
    assert match, f"no GEIST TOKENS block in {page}"
    return re.sub(r"\s+", " ", match.group(0)).strip()


class DesignTokensTest(unittest.TestCase):
    def test_landing_and_app_share_the_same_design_tokens(self) -> None:
        self.assertEqual(
            _token_block(LANDING),
            _token_block(APP),
            "the GEIST TOKENS blocks in site/index.html and "
            "src/framecredit/static/index.html have drifted apart",
        )


if __name__ == "__main__":
    unittest.main()
