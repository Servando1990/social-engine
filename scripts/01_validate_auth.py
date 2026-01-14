"""Validate Publer API credentials."""

from __future__ import annotations

import os
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
    """Run a simple auth validation call."""
    load_dotenv()
    api_key = load_api_key()
    workspace_id = load_workspace_id()
    client = PublerClient(PublerClientConfig(api_key=api_key, workspace_id=workspace_id))
    response = client.get_me()
    print("Auth OK:", response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
