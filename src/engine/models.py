"""Shared data models for the content pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceItem:
    """Normalized content item pulled from a source."""

    source_name: str
    path: Path
    title: str
    body: str


@dataclass(frozen=True)
class Draft:
    """Draft content for a platform."""

    platform: str
    title: str
    body: str
    source_path: Path
