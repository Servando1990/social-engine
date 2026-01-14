"""Scheduling utilities for Publer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from src.publer.client import PublerClient


@dataclass(frozen=True)
class ScheduleRequest:
    """Schedule payload wrapper."""

    network: str
    account_id: str
    text: str
    scheduled_at: Optional[str] = None
    comments: Optional[list[dict[str, Any]]] = None


class PublerScheduler:
    """Create scheduled or immediate posts."""

    def __init__(self, client: PublerClient) -> None:
        self._client = client

    def schedule(self, request: ScheduleRequest) -> dict[str, Any]:
        """Schedule a post (or publish immediately if scheduled_at is None)."""
        payload = {
            "bulk": {
                "state": "scheduled",
                "posts": [
                    {
                        "networks": {request.network: {"type": "status", "text": request.text}},
                        "accounts": [
                            {
                                "id": request.account_id,
                                "scheduled_at": request.scheduled_at,
                                "comments": request.comments or [],
                            }
                        ],
                    }
                ],
            }
        }
        return self._client.post("/posts/schedule", payload)
