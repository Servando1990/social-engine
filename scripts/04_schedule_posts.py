"""Schedule drafts using Publer."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from src.publer.client import PublerClient, PublerClientConfig
from src.publer.scheduler import PublerScheduler, ScheduleRequest


def parse_draft(path: Path) -> tuple[str, str]:
    """Parse a draft file into platform and text."""
    lines = path.read_text().splitlines()
    platform = "linkedin"
    body_lines = []
    for line in lines:
        if line.startswith("Platform:"):
            platform = line.split(":", 1)[1].strip()
            continue
        if line.startswith("# "):
            continue
        if line.startswith("Source:"):
            continue
        body_lines.append(line)
    text = "\n".join([line for line in body_lines if line.strip()])
    return platform, text.strip()


def load_env_value(key: str) -> str:
    """Load an environment variable or raise."""
    value = os.getenv(key, "").strip()
    if not value:
        raise ValueError(f"{key} is missing in .env")
    return value


def main() -> int:
    """Schedule all drafts in the drafts folder."""
    parser = argparse.ArgumentParser(description="Schedule drafts")
    parser.add_argument("--dry-run", action="store_true", help="Print payloads only")
    args = parser.parse_args()

    load_dotenv()
    api_key = load_env_value("PUBLER_API_KEY")
    workspace_id = os.getenv("PUBLER_WORKSPACE_ID", "").strip() or None
    dry_run = args.dry_run or os.getenv("PUBLER_DRY_RUN", "1") == "1"

    client = PublerClient(PublerClientConfig(api_key=api_key, workspace_id=workspace_id))
    scheduler = PublerScheduler(client)

    drafts_dir = Path("drafts")
    if not drafts_dir.exists():
        raise FileNotFoundError("drafts/ not found. Run 03_generate_drafts.py first.")

    for draft_file in drafts_dir.glob("*.md"):
        platform, text = parse_draft(draft_file)
        if platform == "twitter":
            account_id = load_env_value("PUBLER_X_ACCOUNT_ID")
            network = "twitter"
        else:
            account_id = load_env_value("PUBLER_LINKEDIN_ACCOUNT_ID")
            network = "linkedin"

        request = ScheduleRequest(network=network, account_id=account_id, text=text)
        if dry_run:
            print(f"[DRY RUN] Would schedule {draft_file.name} to {network}")
            continue
        response = scheduler.schedule(request)
        print(f"Scheduled {draft_file.name}: {response}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
