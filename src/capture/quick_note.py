"""Quick note capture utility."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class QuickNoteCapture:
    """Append timestamped notes to a local text file."""

    notes_path: Path

    def append_note(self, text: str) -> None:
        """Append a note to the notes file."""
        self.notes_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        line = f"[{timestamp}] {text.strip()}\n"
        self.notes_path.write_text(
            self.notes_path.read_text() + line if self.notes_path.exists() else line
        )
