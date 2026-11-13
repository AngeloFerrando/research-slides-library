import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

from scripts.generate_catalog import discover


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.slides = Path(self.temp.name)

    def folder(self, name, html):
        folder = self.slides / name
        folder.mkdir(parents=True)
        (folder / "index.html").write_text(html, encoding="utf-8")
        return folder

    def test_title_fallback_and_encoded_url(self):
        self.folder("paper #1 & café", "<title> A &amp; B\n Research </title>")
        self.folder("missing_title", "<h1>Hi</h1>")
        items = discover(self.slides)
        self.assertEqual(items[0]["title"], "missing title")
        self.assertEqual(items[1]["title"], "A & B Research")
        self.assertEqual(items[1]["url"], "slides/paper%20%231%20%26%20caf%C3%A9/index.html")
        self.assertTrue((self.slides.parent / unquote(items[1]["url"].replace("slides/", self.slides.name + "/", 1))).is_file())

    def test_metadata_and_standalone(self):
        folder = self.folder("paper", "<title>Original</title>")
        (folder / "metadata.json").write_text(json.dumps({"title": "Override", "authors": ["A", "B"], "year": 2025, "tags": ["AI"]}))
        (self.slides / "stand alone.html").write_text("<title>Standalone</title>")
        (self.slides / "ignored.txt").write_text("ignored")
        items = discover(self.slides)
        self.assertEqual(items[0]["title"], "Override")
        self.assertEqual(items[0]["authors"], ["A", "B"])
        self.assertEqual(items[1]["url"], "slides/stand%20alone.html")

    def test_add_remove_and_rename(self):
        folder = self.folder("old-name", "<title>Paper</title>")
        self.assertEqual(len(discover(self.slides)), 1)
        folder.rename(self.slides / "new-name")
        self.assertEqual(discover(self.slides)[0]["url"], "slides/new-name/index.html")
        (self.slides / "new-name" / "index.html").unlink()
        self.assertEqual(discover(self.slides), [])

    def test_nested_presentations_infer_year_and_keep_metadata_override(self):
        self.folder("2026/FMAS", "<title>FMAS</title>")
        folder = self.folder("2025/ICFEM", "<title>ICFEM</title>")
        (folder / "metadata.json").write_text(json.dumps({"year": 2024}))

        items = discover(self.slides)

        self.assertEqual(items[0]["url"], "slides/2025/ICFEM/index.html")
        self.assertEqual(items[0]["year"], 2024)
        self.assertEqual(items[1]["url"], "slides/2026/FMAS/index.html")
        self.assertEqual(items[1]["year"], "2026")

    def test_invalid_metadata_reports_failure(self):
        folder = self.folder("paper", "<title>Paper</title>")
        (folder / "metadata.json").write_text('{"tags": "not a list"}')
        with self.assertRaisesRegex(ValueError, "tags must be a list"):
            discover(self.slides)

    def test_empty_metadata_title_uses_html(self):
        folder = self.folder("paper", "<title>HTML title</title>")
        (folder / "metadata.json").write_text('{"title": " "}')
        self.assertEqual(discover(self.slides)[0]["title"], "HTML title")


if __name__ == "__main__":
    unittest.main()
