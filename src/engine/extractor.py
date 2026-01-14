"""Extract insights from source items."""

from __future__ import annotations

from dataclasses import dataclass

from src.engine.models import SourceItem


@dataclass(frozen=True)
class ContentExtractor:
    """Simple extractor that trims source text."""

    max_chars: int = 800

    def extract(self, item: SourceItem) -> SourceItem:
        """Return a trimmed copy of the source item."""
        trimmed = item.body.strip()[: self.max_chars]
        return SourceItem(
            source_name=item.source_name,
            path=item.path,
            title=item.title,
            body=trimmed,
        )
