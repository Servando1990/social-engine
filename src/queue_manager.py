"""Queue manager for viewing and managing Publer scheduled posts."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
import requests

STATE_DIR = Path("state")
SNAPSHOT_FILE = STATE_DIR / "publer_snapshot.json"
EVENT_LOG_FILE = STATE_DIR / "queue_events.json"

BASE_URL = "https://app.publer.com/api/v1"
WORKSPACE_ID = "69717f7a2820f00c7aec83f3"


def _load_env() -> None:
    """Load environment variables from config/.env."""
    load_dotenv(dotenv_path="config/.env")


def _get_headers() -> dict[str, str]:
    """Get API headers."""
    _load_env()
    api_key = os.getenv("PUBLER_API_KEY", "")
    return {
        "Authorization": f"Bearer-API {api_key}",
        "Publer-Workspace-Id": WORKSPACE_ID,
        "Content-Type": "application/json",
    }


def _get_accounts() -> list[dict[str, Any]]:
    """Fetch all connected accounts."""
    response = requests.get(f"{BASE_URL}/accounts", headers=_get_headers())
    response.raise_for_status()
    return response.json()


def _get_account_id(platform: str) -> str:
    """Get account ID for a platform (x, linkedin, etc.)."""
    accounts = _get_accounts()
    platform_map = {"x": "twitter", "twitter": "twitter", "linkedin": "linkedin"}
    target = platform_map.get(platform.lower(), platform.lower())
    
    for account in accounts:
        if account.get("provider", "").lower() == target:
            return account.get("id")
    
    raise ValueError(f"No account found for {platform}")


def _log_event(event_type: str, data: dict[str, Any]) -> None:
    """Append an event to the event log."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    events = []
    if EVENT_LOG_FILE.exists():
        try:
            events = json.loads(EVENT_LOG_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            events = []
    events.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event_type,
        "data": data,
    })
    EVENT_LOG_FILE.write_text(json.dumps(events, indent=2))


class QueueManager:
    """Manage Publer scheduled posts queue."""

    def __init__(self) -> None:
        self._accounts_cache: Optional[list[dict]] = None

    def _get_account_ids(self) -> dict[str, str]:
        """Get account IDs by platform (fetched dynamically)."""
        if self._accounts_cache is None:
            self._accounts_cache = _get_accounts()
        
        result = {}
        for account in self._accounts_cache:
            provider = account.get("provider", "").lower()
            if provider == "twitter":
                result["x"] = account.get("id")
                result["twitter"] = account.get("id")
            elif provider == "linkedin":
                result["linkedin"] = account.get("id")
        return result

    def list_scheduled(self, platform: Optional[str] = None) -> list[dict[str, Any]]:
        """
        List scheduled posts, optionally filtered by platform.

        Args:
            platform: Optional platform filter ('linkedin', 'x', 'twitter')

        Returns:
            List of posts with id, text, scheduled_at, platform/network
        """
        params: dict[str, Any] = {"state": "scheduled"}

        if platform:
            account_ids = self._get_account_ids()
            account_id = account_ids.get(platform.lower())
            if account_id:
                params["account_ids[]"] = account_id

        response = requests.get(f"{BASE_URL}/posts", headers=_get_headers(), params=params)
        response.raise_for_status()
        data = response.json()

        posts = data if isinstance(data, list) else data.get("posts", [])

        result = []
        for post in posts:
            result.append({
                "id": post.get("id"),
                "text": post.get("text", post.get("content", "")),
                "scheduled_at": post.get("scheduled_at", post.get("send_at")),
                "network": post.get("network", post.get("provider", "unknown")),
                "platform": post.get("network", post.get("provider", "unknown")),
            })
        return result

    def sync(self) -> dict[str, Any]:
        """
        Fetch all scheduled posts from Publer and save to state/publer_snapshot.json.

        Returns:
            Summary of synced posts per platform
        """
        account_ids = self._get_account_ids()
        all_posts: list[dict[str, Any]] = []
        counts = {"linkedin": 0, "twitter": 0}

        for platform in ["linkedin", "x"]:
            account_id = account_ids.get(platform)
            if not account_id:
                continue
            try:
                params = {"state": "scheduled", "account_ids[]": account_id}
                response = requests.get(f"{BASE_URL}/posts", headers=_get_headers(), params=params)
                response.raise_for_status()
                data = response.json()
                posts = data if isinstance(data, list) else data.get("posts", [])
                for post in posts:
                    post["_platform"] = platform
                all_posts.extend(posts)
                key = "twitter" if platform == "x" else platform
                counts[key] = len(posts)
            except Exception:
                pass

        STATE_DIR.mkdir(parents=True, exist_ok=True)
        snapshot = {
            "synced_at": datetime.utcnow().isoformat() + "Z",
            "posts": all_posts,
            "counts": counts,
        }
        SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2))

        _log_event("sync", {"post_count": len(all_posts), "counts": counts})

        return counts

    def cancel(self, post_id: str) -> dict[str, Any]:
        """
        Cancel/delete a scheduled post.

        Args:
            post_id: The Publer post ID to cancel

        Returns:
            Result of the cancellation attempt
        """
        try:
            response = requests.delete(f"{BASE_URL}/posts/{post_id}", headers=_get_headers())
            response.raise_for_status()
            _log_event("cancel", {"post_id": post_id, "success": True})
            return {"success": True, "post_id": post_id, "message": "Post cancelled"}
        except Exception as e:
            _log_event("cancel", {"post_id": post_id, "success": False, "error": str(e)})
            return {"success": False, "post_id": post_id, "error": str(e)}

    def reschedule(self, post_id: str, new_time: str) -> dict[str, Any]:
        """
        Reschedule a post to a new time.

        Args:
            post_id: The Publer post ID to reschedule
            new_time: New scheduled time (ISO format)

        Returns:
            Result of the reschedule attempt
        """
        try:
            payload = {"scheduled_at": new_time}
            response = requests.put(
                f"{BASE_URL}/posts/{post_id}",
                headers=_get_headers(),
                json=payload
            )
            response.raise_for_status()
            _log_event("reschedule", {
                "post_id": post_id,
                "new_time": new_time,
                "success": True,
            })
            return {
                "success": True,
                "post_id": post_id,
                "new_time": new_time,
                "message": "Post rescheduled",
            }
        except Exception as e:
            _log_event("reschedule", {
                "post_id": post_id,
                "new_time": new_time,
                "success": False,
                "error": str(e),
            })
            return {"success": False, "post_id": post_id, "error": str(e)}
