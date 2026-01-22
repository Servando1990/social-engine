"""State management for social-engine.

Manages:
- state/events.jsonl: Append-only event log
- state/local_index.json: draft → publer_post_id mapping
- state/publer_snapshot.json: Cached queue from Publer
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

STATE_DIR = Path(__file__).parent.parent / "state"


@dataclass
class Event:
    timestamp: str
    event_type: str
    data: dict

    @classmethod
    def create(cls, event_type: str, data: dict) -> "Event":
        return cls(
            timestamp=datetime.utcnow().isoformat() + "Z",
            event_type=event_type,
            data=data,
        )


@dataclass
class ScheduledPost:
    draft_id: str
    publer_post_id: str
    platform: str
    scheduled_at: Optional[str] = None
    status: str = "scheduled"


def _ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def log_event(event_type: str, data: dict) -> Event:
    """Append an event to events.jsonl."""
    _ensure_state_dir()
    event = Event.create(event_type, data)
    events_file = STATE_DIR / "events.jsonl"
    with open(events_file, "a") as f:
        f.write(json.dumps(asdict(event)) + "\n")
    return event


def get_local_index() -> dict[str, str]:
    """Get the draft → publer_post_id mapping."""
    _ensure_state_dir()
    index_file = STATE_DIR / "local_index.json"
    if not index_file.exists():
        return {}
    with open(index_file) as f:
        return json.load(f)


def update_local_index(draft_id: str, publer_post_id: str) -> None:
    """Update the local index with a new mapping."""
    _ensure_state_dir()
    index = get_local_index()
    index[draft_id] = publer_post_id
    index_file = STATE_DIR / "local_index.json"
    with open(index_file, "w") as f:
        json.dump(index, f, indent=2)
    log_event("index_updated", {"draft_id": draft_id, "publer_post_id": publer_post_id})


def get_snapshot() -> dict:
    """Get the cached Publer queue snapshot."""
    _ensure_state_dir()
    snapshot_file = STATE_DIR / "publer_snapshot.json"
    if not snapshot_file.exists():
        return {"posts": [], "fetched_at": None}
    with open(snapshot_file) as f:
        return json.load(f)


def save_snapshot(posts: list[dict]) -> None:
    """Save a new Publer queue snapshot."""
    _ensure_state_dir()
    snapshot = {
        "posts": posts,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
    }
    snapshot_file = STATE_DIR / "publer_snapshot.json"
    with open(snapshot_file, "w") as f:
        json.dump(snapshot, f, indent=2)
    log_event("snapshot_saved", {"post_count": len(posts)})
