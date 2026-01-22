"""Schedule planner for approved drafts."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from zoneinfo import ZoneInfo

from dotenv import load_dotenv
import requests

PROJECT_ROOT = Path(__file__).parent.parent
QUEUE_DIR = PROJECT_ROOT / "queue"
DRAFTS_DIR = PROJECT_ROOT / "drafts"
STATE_DIR = PROJECT_ROOT / "state"

env_path = PROJECT_ROOT / "config" / ".env"
load_dotenv(env_path)

BASE_URL = "https://app.publer.com/api/v1"
WORKSPACE_ID = "69717f7a2820f00c7aec83f3"

_accounts_cache: Optional[list[dict]] = None


def _get_headers() -> dict[str, str]:
    """Get API headers."""
    api_key = os.getenv("PUBLER_API_KEY", "")
    return {
        "Authorization": f"Bearer-API {api_key}",
        "Publer-Workspace-Id": WORKSPACE_ID,
        "Content-Type": "application/json",
    }


def _get_accounts() -> list[dict[str, Any]]:
    """Fetch all connected accounts (cached)."""
    global _accounts_cache
    if _accounts_cache is None:
        response = requests.get(f"{BASE_URL}/accounts", headers=_get_headers())
        response.raise_for_status()
        _accounts_cache = response.json()
    return _accounts_cache


def _get_account_id(platform: str) -> str:
    """Get account ID for platform by fetching from API."""
    accounts = _get_accounts()
    platform_map = {"x": "twitter", "twitter": "twitter", "linkedin": "linkedin"}
    target = platform_map.get(platform.lower(), platform.lower())
    
    for account in accounts:
        if account.get("provider", "").lower() == target:
            return account.get("id")
    
    raise ValueError(f"No account found for {platform}")


def _get_network(platform: str) -> str:
    """Map platform to Publer network name."""
    platform_lower = platform.lower()
    if platform_lower in ("x", "twitter"):
        return "twitter"
    return platform_lower


def _parse_draft_metadata(draft_path: Path) -> dict[str, Any]:
    """Extract metadata from draft file (YAML frontmatter)."""
    content = draft_path.read_text()
    metadata: dict[str, Any] = {"path": str(draft_path), "content": content}
    
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1].strip()
            for line in frontmatter.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip().strip('"').strip("'")
            metadata["body"] = parts[2].strip()
        else:
            metadata["body"] = content
    else:
        metadata["body"] = content
    
    return metadata


def _extract_post_text(metadata: dict[str, Any]) -> str:
    """Extract the actual post text from draft metadata."""
    body = metadata.get("body", metadata.get("content", ""))
    lines = body.strip().split("\n")
    text_lines = []
    in_content = False
    
    for line in lines:
        if line.startswith("#"):
            continue
        if line.strip():
            in_content = True
        if in_content:
            text_lines.append(line)
    
    return "\n".join(text_lines).strip()


def get_approved_drafts(platform: Optional[str] = None) -> list[dict[str, Any]]:
    """Get list of approved drafts, optionally filtered by platform."""
    approved = []
    
    if not DRAFTS_DIR.exists():
        return approved
    
    for draft_file in DRAFTS_DIR.glob("*.md"):
        metadata = _parse_draft_metadata(draft_file)
        status = metadata.get("status", "").lower()
        
        if status != "approved":
            continue
        
        draft_platform = metadata.get("platform", "").lower()
        if platform:
            platform_filter = platform.lower()
            if platform_filter in ("x", "twitter"):
                if draft_platform not in ("x", "twitter"):
                    continue
            elif draft_platform != platform_filter:
                continue
        
        approved.append(metadata)
    
    return approved


def create_plan(
    drafts: list[str],
    platform: str,
    start_date: str,
    start_time: str = "09:00",
    interval_days: int = 1,
    timezone: str = "America/Chicago",
) -> dict[str, Any]:
    """Create a scheduling plan for drafts."""
    tz = ZoneInfo(timezone)
    base_dt = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
    base_dt = base_dt.replace(tzinfo=tz)
    
    account_id = _get_account_id(platform)
    network = _get_network(platform)
    
    items = []
    for i, draft_path in enumerate(drafts):
        scheduled_dt = base_dt + timedelta(days=i * interval_days)
        scheduled_at = scheduled_dt.isoformat()
        
        items.append({
            "draft": draft_path,
            "platform": network,
            "scheduled_at": scheduled_at,
            "account_id": account_id,
        })
    
    return {
        "created_at": datetime.now(tz=ZoneInfo("UTC")).isoformat(),
        "timezone": timezone,
        "items": items,
    }


def create_plan_from_approved(
    platform: Optional[str] = None,
    count: Optional[int] = None,
    start_date: Optional[str] = None,
    start_time: str = "09:00",
    interval_days: int = 1,
    timezone: str = "America/Chicago",
) -> dict[str, Any]:
    """Create plan from approved drafts."""
    approved = get_approved_drafts(platform)
    
    if count:
        approved = approved[:count]
    
    if not approved:
        return {
            "created_at": datetime.now(tz=ZoneInfo("UTC")).isoformat(),
            "timezone": timezone,
            "items": [],
        }
    
    if not start_date:
        tz = ZoneInfo(timezone)
        start_date = (datetime.now(tz) + timedelta(days=1)).strftime("%Y-%m-%d")
    
    tz = ZoneInfo(timezone)
    base_dt = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
    base_dt = base_dt.replace(tzinfo=tz)
    
    items = []
    for i, draft_meta in enumerate(approved):
        draft_path = draft_meta["path"]
        draft_platform = draft_meta.get("platform", platform or "twitter")
        
        account_id = _get_account_id(draft_platform)
        network = _get_network(draft_platform)
        
        scheduled_dt = base_dt + timedelta(days=i * interval_days)
        scheduled_at = scheduled_dt.isoformat()
        
        items.append({
            "draft": draft_path,
            "platform": network,
            "scheduled_at": scheduled_at,
            "account_id": account_id,
        })
    
    return {
        "created_at": datetime.now(tz=ZoneInfo("UTC")).isoformat(),
        "timezone": timezone,
        "items": items,
    }


def save_plan(plan: dict[str, Any], path: Optional[Path] = None) -> Path:
    """Save plan to JSON file."""
    if path is None:
        QUEUE_DIR.mkdir(parents=True, exist_ok=True)
        path = QUEUE_DIR / "plan.json"
    
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=2))
    return path


def load_plan(path: Path) -> dict[str, Any]:
    """Load plan from JSON file."""
    return json.loads(path.read_text())


def _log_event(event_type: str, data: dict[str, Any]) -> None:
    """Log an event to state/events.json."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    events_file = STATE_DIR / "events.json"
    
    events = []
    if events_file.exists():
        try:
            events = json.loads(events_file.read_text())
        except json.JSONDecodeError:
            events = []
    
    events.append({
        "timestamp": datetime.now(tz=ZoneInfo("UTC")).isoformat(),
        "type": event_type,
        "data": data,
    })
    
    events_file.write_text(json.dumps(events, indent=2))


def apply_plan(plan: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
    """Apply a schedule plan, posting each item via Publer API."""
    results: dict[str, Any] = {
        "successes": [],
        "failures": [],
        "dry_run": dry_run,
    }
    
    if not plan.get("items"):
        return results
    
    api_key = os.getenv("PUBLER_API_KEY")
    if not api_key and not dry_run:
        raise ValueError("PUBLER_API_KEY not set in environment")
    
    for item in plan["items"]:
        draft_path = Path(item["draft"])
        platform = item["platform"]
        scheduled_at = item["scheduled_at"]
        account_id = item["account_id"]
        
        if not draft_path.exists():
            results["failures"].append({
                "draft": str(draft_path),
                "error": "Draft file not found",
            })
            continue
        
        metadata = _parse_draft_metadata(draft_path)
        text = _extract_post_text(metadata)
        
        if not text:
            results["failures"].append({
                "draft": str(draft_path),
                "error": "No post text found in draft",
            })
            continue
        
        if dry_run:
            print(f"[DRY RUN] Would schedule:")
            print(f"  Draft: {draft_path}")
            print(f"  Platform: {platform}")
            print(f"  Scheduled: {scheduled_at}")
            print(f"  Text preview: {text[:100]}...")
            print()
            results["successes"].append({
                "draft": str(draft_path),
                "platform": platform,
                "scheduled_at": scheduled_at,
            })
        else:
            try:
                payload = {
                    "bulk": {
                        "state": "scheduled",
                        "posts": [{
                            "networks": {
                                platform: {
                                    "type": "status",
                                    "text": text
                                }
                            },
                            "accounts": [{
                                "id": account_id,
                                "scheduled_at": scheduled_at
                            }]
                        }]
                    }
                }
                
                response = requests.post(
                    f"{BASE_URL}/posts/schedule",
                    headers=_get_headers(),
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                job_id = result.get("job_id")
                if job_id:
                    time.sleep(2)
                    status_resp = requests.get(
                        f"{BASE_URL}/job_status/{job_id}",
                        headers=_get_headers()
                    )
                    status = status_resp.json()
                    failures = status.get("payload", {}).get("failures", {})
                    if failures:
                        results["failures"].append({
                            "draft": str(draft_path),
                            "error": str(failures),
                        })
                        _log_event("schedule_failed", {
                            "draft": str(draft_path),
                            "platform": platform,
                            "error": str(failures),
                        })
                        continue
                
                results["successes"].append({
                    "draft": str(draft_path),
                    "platform": platform,
                    "scheduled_at": scheduled_at,
                    "job_id": job_id,
                })
                _log_event("post_scheduled", {
                    "draft": str(draft_path),
                    "platform": platform,
                    "scheduled_at": scheduled_at,
                    "job_id": job_id,
                })
            except Exception as e:
                results["failures"].append({
                    "draft": str(draft_path),
                    "error": str(e),
                })
                _log_event("schedule_failed", {
                    "draft": str(draft_path),
                    "platform": platform,
                    "error": str(e),
                })
    
    return results
