"""Analytics utilities for Publer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.publer.client import PublerClient


@dataclass(frozen=True)
class AnalyticsRequest:
    """Analytics request parameters."""

    account_id: str
    date_from: str
    date_to: str


class PublerAnalytics:
    """Fetch analytics from Publer."""

    def __init__(self, client: PublerClient) -> None:
        self._client = client

    def post_insights(self, request: AnalyticsRequest) -> dict[str, Any]:
        """Fetch post insights for an account."""
        path = f"/analytics/{request.account_id}/post_insights"
        return self._client.get(path, params={"from": request.date_from, "to": request.date_to})
