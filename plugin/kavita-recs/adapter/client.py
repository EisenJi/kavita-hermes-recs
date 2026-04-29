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

    def _request_json(self, method: str, path: str, body: Any | None = None) -> Any:
        url = urljoin(self._base_url, path.lstrip("/"))
        data = None
        headers = {
            "Accept": "application/json",
            "x-api-key": self._settings.kavita_api_key or "",
        }
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = Request(
            url,
            method=method,
            headers=headers,
            data=data,
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

    def list_libraries(self) -> list[dict[str, Any]]:
        data = self._request_json("GET", "/api/Library/libraries")
        if not isinstance(data, list):
            raise KavitaClientError("Unexpected libraries response shape from Kavita.")
        return data

    def list_series_page(self, page_number: int, page_size: int) -> list[dict[str, Any]]:
        data = self._request_json(
            "POST",
            f"/api/Series/all-v2?PageNumber={page_number}&PageSize={page_size}",
            body={},
        )
        if not isinstance(data, list):
            raise KavitaClientError("Unexpected series response shape from Kavita.")
        return data

    def list_all_series(self, page_size: int = 100) -> list[dict[str, Any]]:
        page = 1
        all_items: list[dict[str, Any]] = []
        while True:
            items = self.list_series_page(page_number=page, page_size=page_size)
            all_items.extend(items)
            if len(items) < page_size:
                break
            page += 1
        return all_items

    def list_filtered_series_page(self, filter_body: dict[str, Any], page_number: int, page_size: int) -> list[dict[str, Any]]:
        data = self._request_json(
            "POST",
            f"/api/Series/v2?PageNumber={page_number}&PageSize={page_size}",
            body=filter_body,
        )
        if not isinstance(data, list):
            raise KavitaClientError("Unexpected filtered series response shape from Kavita.")
        return data

    def list_all_filtered_series(self, filter_body: dict[str, Any], page_size: int = 100) -> list[dict[str, Any]]:
        page = 1
        all_items: list[dict[str, Any]] = []
        while True:
            items = self.list_filtered_series_page(filter_body=filter_body, page_number=page, page_size=page_size)
            all_items.extend(items)
            if len(items) < page_size:
                break
            page += 1
        return all_items

    def get_continue_point(self, series_id: int) -> dict[str, Any]:
        data = self._request_json("GET", f"/api/Reader/continue-point?seriesId={series_id}")
        if not isinstance(data, dict):
            raise KavitaClientError(f"Unexpected continue-point response shape for series {series_id}.")
        return data

    def list_reading_lists(self, page_size: int = 100) -> list[dict[str, Any]]:
        data = self._request_json(
            "POST",
            f"/api/ReadingList/lists?PageNumber=1&PageSize={page_size}&includePromoted=false&sortByLastModified=true",
            body={},
        )
        if not isinstance(data, list):
            raise KavitaClientError("Unexpected reading list response shape from Kavita.")
        return data

    def create_reading_list(self, title: str) -> dict[str, Any]:
        data = self._request_json(
            "POST",
            "/api/ReadingList/create",
            body={"title": title},
        )
        if not isinstance(data, dict):
            raise KavitaClientError("Unexpected reading list create response shape from Kavita.")
        return data

    def add_series_to_reading_list(self, reading_list_id: int, series_id: int) -> None:
        self._request_json(
            "POST",
            "/api/ReadingList/update-by-series",
            body={"readingListId": reading_list_id, "seriesId": series_id},
        )
