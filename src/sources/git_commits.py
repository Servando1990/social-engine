"""Git commit source reader."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from src.engine.models import SourceItem


@dataclass(frozen=True)
class GitCommitsConfig:
    """Configuration for git commit scanning."""

    name: str
    repo_path: Path
    max_commits: int


class GitCommitsSource:
    """Collect recent git commit messages."""

    def __init__(self, config: GitCommitsConfig) -> None:
        self._config = config

    def collect(self) -> list[SourceItem]:
        """Collect recent commits as source items."""
        if not (self._config.repo_path / ".git").exists():
            return []
        try:
            output = subprocess.check_output(
                [
                    "git",
                    "-C",
                    str(self._config.repo_path),
                    "log",
                    f"-n{self._config.max_commits}",
                    "--pretty=%s",
                ],
                text=True,
            )
        except subprocess.CalledProcessError:
            return []

        items = []
        for idx, line in enumerate(output.splitlines(), start=1):
            title = line.strip()
            if not title:
                continue
            items.append(
                SourceItem(
                    source_name=self._config.name,
                    path=self._config.repo_path,
                    title=f"Commit {idx}",
                    body=title,
                )
            )
        return items
