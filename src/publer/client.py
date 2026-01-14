"""Publer API client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

import requests


@dataclass(frozen=True)
class PublerClientConfig:
    """Configuration for Publer API client."""

    api_key: str
    workspace_id: Optional[str] = None
    base_url: str = "https://app.publer.com/api/v1"


class PublerClient:
    """Minimal Publer API client using bearer token auth."""

    def __init__(self, config: PublerClientConfig) -> None:
        self._config = config

    def get_me(self) -> dict[str, Any]:
        """Validate credentials by fetching current user."""
        return self.get("/me")

    def list_workspaces(self) -> dict[str, Any]:
        """List available workspaces."""
        return self.get("/workspaces")

    def list_accounts(self) -> dict[str, Any]:
        """List connected social accounts."""
        return self.get("/accounts")

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Perform a GET request."""
        return self._request("GET", path, params=params)

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Perform a POST request."""
        return self._request("POST", path, json=payload)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        url = f"{self._config.base_url}{path}"
        headers = {
            "Authorization": f"Bearer-API {self._config.api_key}",
            "Content-Type": "application/json",
        }
        if self._config.workspace_id:
            headers["Publer-Workspace-Id"] = self._config.workspace_id

        response = requests.request(
            method=method, url=url, headers=headers, params=params, json=json, timeout=30
        )
        response.raise_for_status()
        return response.json()
