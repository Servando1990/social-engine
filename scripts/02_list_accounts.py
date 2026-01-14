"""List Publer accounts and save a local snapshot."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from src.publer.client import PublerClient, PublerClientConfig


def load_api_key() -> str:
    """Load the Publer API key from environment."""
    api_key = os.getenv("PUBLER_API_KEY", "").strip()
    if not api_key:
        raise ValueError("PUBLER_API_KEY is missing in .env")
    return api_key


def load_workspace_id() -> Optional[str]:
    """Load optional workspace ID from environment."""
    workspace_id = os.getenv("PUBLER_WORKSPACE_ID", "").strip()
    return workspace_id or None


def main() -> int:
    """Fetch accounts and store them in state/accounts.json."""
    load_dotenv()
    client = PublerClient(
        PublerClientConfig(api_key=load_api_key(), workspace_id=load_workspace_id())
    )
    response = client.list_accounts()
    print(json.dumps(response, indent=2))

    output_path = Path("state/accounts.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(response, indent=2))
    print(f"Saved to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
