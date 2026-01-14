"""Fetch Publer analytics for an account."""

from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv

from src.publer.analytics import AnalyticsRequest, PublerAnalytics
from src.publer.client import PublerClient, PublerClientConfig


def load_env_value(key: str) -> str:
    """Load an environment variable or raise."""
    value = os.getenv(key, "").strip()
    if not value:
        raise ValueError(f"{key} is missing in .env")
    return value


def main() -> int:
    """Fetch analytics for the requested account."""
    parser = argparse.ArgumentParser(description="Fetch post insights")
    parser.add_argument("--account-id", type=str, required=False)
    parser.add_argument("--from", dest="date_from", type=str, required=True)
    parser.add_argument("--to", dest="date_to", type=str, required=True)
    args = parser.parse_args()

    load_dotenv()
    api_key = load_env_value("PUBLER_API_KEY")
    workspace_id = os.getenv("PUBLER_WORKSPACE_ID", "").strip() or None
    account_id = args.account_id or load_env_value("PUBLER_LINKEDIN_ACCOUNT_ID")

    client = PublerClient(PublerClientConfig(api_key=api_key, workspace_id=workspace_id))
    analytics = PublerAnalytics(client)
    response = analytics.post_insights(
        AnalyticsRequest(account_id=account_id, date_from=args.date_from, date_to=args.date_to)
    )
    print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
