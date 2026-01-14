"""Generate drafts from extracted source items."""

from __future__ import annotations

from dataclasses import dataclass

from src.engine.models import Draft, SourceItem


@dataclass(frozen=True)
class ContentGenerator:
    """Generate basic drafts for LinkedIn and X."""

    def generate(self, item: SourceItem) -> list[Draft]:
        """Generate a LinkedIn and X draft from a source item."""
        linkedin_body = self._linkedin_template(item)
        twitter_body = self._twitter_template(item)
        return [
            Draft(
                platform="linkedin",
                title=f"{item.title} (LinkedIn)",
                body=linkedin_body,
                source_path=item.path,
            ),
            Draft(
                platform="twitter",
                title=f"{item.title} (X)",
                body=twitter_body,
                source_path=item.path,
            ),
        ]

    def _linkedin_template(self, item: SourceItem) -> str:
        return (
            f"{item.title}\n\n"
            "Here is the core insight:\n"
            f"{item.body}\n\n"
            "Takeaway:\n"
            "- What changed\n"
            "- Why it matters\n"
            "- What I would do next\n"
        )

    def _twitter_template(self, item: SourceItem) -> str:
        return (
            f"{item.title}\n\n"
            "Quick insight:\n"
            f"{item.body}\n\n"
            "Thread idea:\n"
            "1/ Problem\n"
            "2/ Approach\n"
            "3/ Result\n"
            "4/ Lesson\n"
        )
