"""Minimal HTTP client for Kavita."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from ..config import Settings


class KavitaClientError(RuntimeError):
    """Raised when the Kavita API call fails."""


@dataclass(slots=True)
class KavitaAccount:
    id: int | None
    username: str | None
    email: str | None


class KavitaClient:
    """Very small Kavita client built on the standard library."""

    def __init__(self, settings: Settings):
        if not settings.kavita_base_url:
            raise KavitaClientError("KAVITA_BASE_URL is not configured.")
        if not settings.kavita_api_key:
            raise KavitaClientError("KAVITA_API_KEY is not configured.")
        self._settings = settings
        self._base_url = settings.kavita_base_url.rstrip("/") + "/"

    def _request_json(self, method: str, path: str) -> Any:
        url = urljoin(self._base_url, path.lstrip("/"))
        request = Request(
            url,
            method=method,
            headers={
                "Accept": "application/json",
                "x-api-key": self._settings.kavita_api_key or "",
            },
        )
        try:
            with urlopen(request, timeout=self._settings.kavita_timeout_seconds) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as exc:
            raise KavitaClientError(f"Kavita API returned HTTP {exc.code} for {path}") from exc
        except URLError as exc:
            raise KavitaClientError(f"Unable to reach Kavita at {self._base_url}: {exc.reason}") from exc

        if not payload:
            return None
        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise KavitaClientError(f"Kavita returned invalid JSON for {path}") from exc

    def get_current_user(self) -> KavitaAccount:
        data = self._request_json("GET", "/api/Account")
        if not isinstance(data, dict):
            raise KavitaClientError("Unexpected Account response shape from Kavita.")
        return KavitaAccount(
            id=data.get("id"),
            username=data.get("username"),
            email=data.get("email"),
        )

    def ping(self) -> bool:
        self.get_current_user()
        return True
