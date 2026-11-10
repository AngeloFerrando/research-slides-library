#!/usr/bin/env python3
"""Generate a static catalog from the top-level entries in slides/."""

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.finished = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title" and not self.finished:
            self.in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title" and self.in_title:
            self.in_title = False
            self.finished = True

    def handle_data(self, data):
        if self.in_title:
            self.parts.append(data)


def fallback_title(name):
    return re.sub(r"[-_]+", " ", name).strip() or name


def metadata_for(folder):
    path = folder / "metadata.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"{path}: cannot read metadata: {error}") from error
    if not isinstance(data, dict):
        raise ValueError(f"{path}: metadata must be a JSON object")
    for key in ("title", "description", "date"):
        if key in data and not isinstance(data[key], str):
            raise ValueError(f"{path}: {key} must be a string")
    if "year" in data and (isinstance(data["year"], bool) or not isinstance(data["year"], (int, str))):
        raise ValueError(f"{path}: year must be a number or string")
    if "authors" in data and not (
        isinstance(data["authors"], str)
        or isinstance(data["authors"], list) and all(isinstance(x, str) for x in data["authors"])
    ):
        raise ValueError(f"{path}: authors must be a string or list of strings")
    if "tags" in data and not (isinstance(data["tags"], list) and all(isinstance(x, str) for x in data["tags"])):
        raise ValueError(f"{path}: tags must be a list of strings")
    return {key: data[key] for key in ("title", "authors", "year", "description", "tags", "date") if key in data}


def discover(slides):
    if not slides.is_dir():
        raise ValueError(f"Slides directory not found: {slides}")
    entries = []
    for item in sorted(slides.iterdir(), key=lambda p: p.name.casefold()):
        if item.is_dir() and (item / "index.html").is_file():
            html = item / "index.html"
            path = f"slides/{quote(item.name, safe='')}/index.html"
            name = item.name
            metadata = metadata_for(item)
        elif item.is_file() and item.suffix.lower() == ".html":
            html = item
            path = f"slides/{quote(item.name, safe='')}"
            name = item.stem
            metadata = {}
        else:
            continue
        parser = TitleParser()
        try:
            parser.feed(html.read_text(encoding="utf-8-sig"))
        except (OSError, UnicodeError) as error:
            raise ValueError(f"{html}: cannot read presentation: {error}") from error
        title = " ".join("".join(parser.parts).split())
        metadata["title"] = metadata.get("title", "").strip() or title or fallback_title(name)
        metadata["url"] = path
        entries.append(metadata)
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slides", type=Path, default=ROOT / "slides")
    parser.add_argument("--output", type=Path, default=ROOT / "website" / "catalog.json")
    args = parser.parse_args()
    try:
        entries = discover(args.slides)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError) as error:
        print(f"Catalog generation failed: {error}", file=sys.stderr)
        return 1
    print(f"Generated {args.output} with {len(entries)} presentations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
