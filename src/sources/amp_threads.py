"""Amp threads source placeholder."""

from __future__ import annotations

from dataclasses import dataclass

from src.engine.models import SourceItem


@dataclass(frozen=True)
class AmpThreadsConfig:
    """Configuration for Amp threads source."""

    name: str
    filters: str


class AmpThreadsSource:
    """Placeholder source for Amp threads."""

    def __init__(self, config: AmpThreadsConfig) -> None:
        self._config = config

    def collect(self) -> list[SourceItem]:
        """Return no items until Amp integration is added."""
        _ = self._config
        return []
