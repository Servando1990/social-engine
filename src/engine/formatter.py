"""Format drafts into file-friendly output."""

from __future__ import annotations

from dataclasses import dataclass

from src.engine.models import Draft


@dataclass(frozen=True)
class ContentFormatter:
    """Format drafts into markdown text."""

    def format(self, draft: Draft) -> str:
        """Return markdown content for a draft."""
        return (
            f"# {draft.title}\n\n"
            f"Platform: {draft.platform}\n"
            f"Source: {draft.source_path}\n\n"
            f"{draft.body}\n"
        )
