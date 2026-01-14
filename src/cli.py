"""Command-line interface for the Social Engine."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from src.capture.quick_note import QuickNoteCapture


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Social Engine CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    note_parser = subparsers.add_parser("note", help="Capture a quick idea")
    note_parser.add_argument("text", type=str, help="Idea text")
    note_parser.add_argument(
        "--output",
        type=str,
        default="state/quick_notes.txt",
        help="Path to the notes file",
    )

    return parser


def run_note(text: str, output: str) -> int:
    """Append a quick note to the notes file."""
    capture = QuickNoteCapture(notes_path=Path(output))
    capture.append_note(text=text)
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "note":
        return run_note(text=args.text, output=args.output)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
