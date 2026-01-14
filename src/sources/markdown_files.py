"""Markdown source reader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from src.engine.models import SourceItem


@dataclass(frozen=True)
class MarkdownSourceConfig:
    """Configuration for markdown source scanning."""

    name: str
    paths: list[Path]
    glob: str
    max_files: int


class MarkdownSource:
    """Collect markdown files from configured paths."""

    def __init__(self, config: MarkdownSourceConfig) -> None:
        self._config = config

    def collect(self) -> list[SourceItem]:
        """Collect markdown files as source items."""
        files = list(self._iter_files())
        limited = files[: self._config.max_files]
        return [self._to_item(path) for path in limited]

    def _iter_files(self) -> Iterable[Path]:
        for root in self._config.paths:
            if not root.exists():
                continue
            for path in root.glob(self._config.glob):
                if path.is_file():
                    yield path

    def _to_item(self, path: Path) -> SourceItem:
        text = path.read_text(errors="ignore")
        title = path.stem.replace("-", " ").strip()
        body = text.strip()
        return SourceItem(
            source_name=self._config.name,
            path=path,
            title=title,
            body=body,
        )
