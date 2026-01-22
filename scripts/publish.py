#!/usr/bin/env python3
"""Publish posts to social media via Publer API."""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import requests

# Load environment variables
env_path = Path(__file__).parent.parent / "config" / ".env"
load_dotenv(env_path)

API_KEY = os.getenv("PUBLER_API_KEY")
WORKSPACE_ID = "69717f7a2820f00c7aec83f3"
BASE_URL = "https://app.publer.com/api/v1"


def get_headers():
    return {
        "Authorization": f"Bearer-API {API_KEY}",
        "Publer-Workspace-Id": WORKSPACE_ID,
        "Content-Type": "application/json"
    }


def get_accounts():
    """Fetch all connected accounts."""
    response = requests.get(f"{BASE_URL}/accounts", headers=get_headers())
    return response.json()


def get_account_id(platform: str) -> str:
    """Get account ID for a platform (x, linkedin, etc.)."""
    accounts = get_accounts()
    platform_map = {"x": "twitter", "twitter": "twitter", "linkedin": "linkedin"}
    target = platform_map.get(platform.lower(), platform.lower())
    
    for account in accounts:
        if account.get("provider", "").lower() == target:
            return account.get("id")
    
    raise ValueError(f"No account found for {platform}. Available: {[a.get('provider') for a in accounts]}")


def check_job_status(job_id: str) -> dict:
    """Check the status of a scheduled post job."""
    response = requests.get(f"{BASE_URL}/job_status/{job_id}", headers=get_headers())
    return response.json()


def publish_post(text: str, platform: str = "x", minutes_from_now: int = 1) -> dict:
    """Publish a post to the specified platform."""
    account_id = get_account_id(platform)
    provider = "twitter" if platform.lower() in ["x", "twitter"] else platform.lower()
    
    schedule_time = (datetime.now(timezone.utc) + timedelta(minutes=minutes_from_now)).strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    response = requests.post(
        f"{BASE_URL}/posts/schedule",
        headers=get_headers(),
        json={
            "bulk": {
                "state": "scheduled",
                "posts": [{
                    "networks": {
                        provider: {
                            "type": "status",
                            "text": text
                        }
                    },
                    "accounts": [{
                        "id": account_id,
                        "scheduled_at": schedule_time
                    }]
                }]
            }
        }
    )
    
    result = response.json()
    
    if "job_id" in result:
        import time
        time.sleep(2)
        status = check_job_status(result["job_id"])
        return {"status": response.status_code, "job_id": result["job_id"], "job_status": status}
    
    return {"status": response.status_code, "response": result}


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "testing publer api - so far so good"
    platform = sys.argv[2] if len(sys.argv) > 2 else "x"
    
    result = publish_post(text, platform)
    print(f"Status: {result['status']}")
    if "job_status" in result:
        failures = result["job_status"].get("payload", {}).get("failures", {})
        if failures:
            print(f"Failures: {failures}")
        else:
            print(f"Success! Job ID: {result['job_id']}")
    else:
        print(f"Response: {result.get('response', result)}")
