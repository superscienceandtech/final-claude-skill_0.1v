import tempfile
import unittest
from pathlib import Path

from scripts.check_markdown_links import markdown_targets, unresolved_links


class MarkdownLinkCheckTests(unittest.TestCase):
    def test_reports_missing_relative_link_with_line_number(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "README.md"
            source.write_text("# Title\n[missing](docs/not-here.md)\n", encoding="utf-8")

            self.assertEqual(
                unresolved_links(root),
                [(Path("README.md"), 2, "docs/not-here.md")],
            )

    def test_accepts_existing_relative_file_and_directory_targets(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            docs = root / "docs"
            docs.mkdir()
            (docs / "guide.md").write_text("# Guide\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[guide](docs/guide.md) [folder](docs/)\n",
                encoding="utf-8",
            )

            self.assertEqual(unresolved_links(root), [])

    def test_ignores_external_links_anchors_and_fenced_code(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "README.md"
            source.write_text(
                "[web](https://example.com) [section](#intro)\n"
                "```markdown\n[example](missing.md)\n```\n"
                "`[inline example](missing.md)`\n",
                encoding="utf-8",
            )

            self.assertEqual(unresolved_links(root), [])

    def test_extracts_image_targets_and_decodes_percent_escapes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "an image.png").write_bytes(b"image")
            source = root / "README.md"
            source.write_text("![image](an%20image.png)\n", encoding="utf-8")

            self.assertEqual(unresolved_links(root), [])
            self.assertEqual(markdown_targets(source), [(1, "an%20image.png")])

    def test_extracts_angle_bracket_destinations(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "file name.md").write_text("# File\n", encoding="utf-8")
            source = root / "README.md"
            source.write_text("[file](<file name.md> \"title\")\n", encoding="utf-8")

            self.assertEqual(unresolved_links(root), [])


if __name__ == "__main__":
    unittest.main()
