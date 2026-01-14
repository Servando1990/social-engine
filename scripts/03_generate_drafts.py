"""Generate drafts from configured sources."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from src.engine.extractor import ContentExtractor
from src.engine.formatter import ContentFormatter
from src.engine.generator import ContentGenerator
from src.sources.markdown_files import MarkdownSource, MarkdownSourceConfig


def load_sources_config(path: Path) -> list[dict[str, Any]]:
    """Load sources config from a YAML file."""
    raw = yaml.safe_load(path.read_text())
    return raw.get("sources", [])


def slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip()).strip("-").lower()
    return slug or "draft"


def main() -> int:
    """Generate drafts into the drafts folder."""
    config_path = Path("config/sources.yml")
    if not config_path.exists():
        raise FileNotFoundError("config/sources.yml not found")

    sources = load_sources_config(config_path)
    extractor = ContentExtractor()
    generator = ContentGenerator()
    formatter = ContentFormatter()

    drafts_path = Path("drafts")
    drafts_path.mkdir(parents=True, exist_ok=True)

    for source in sources:
        if source.get("type") != "markdown":
            continue
        config = MarkdownSourceConfig(
            name=source["name"],
            paths=[Path(p) for p in source["paths"]],
            glob=source.get("glob", "**/*.md"),
            max_files=int(source.get("max_files", 5)),
        )
        collector = MarkdownSource(config)
        items = collector.collect()
        for item in items:
            extracted = extractor.extract(item)
            drafts = generator.generate(extracted)
            for draft in drafts:
                slug = slugify(draft.title)
                file_path = drafts_path / f"{slug}.md"
                file_path.write_text(formatter.format(draft))
                print(f"Wrote {file_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
