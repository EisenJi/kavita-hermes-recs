"""Snapshot sync entrypoints."""

from __future__ import annotations

from dataclasses import asdict

from ..adapter.client import KavitaClient
from ..config import load_settings
from ..storage.db import (
    bootstrap_database,
    log_sync_run,
    replace_want_to_read_flags,
    upsert_libraries,
    upsert_progress_entries,
    upsert_series,
)


WANT_TO_READ_FILTER = {
    "name": "want-to-read",
    "statements": [
        {
            "field": 26,
            "comparison": 0,
            "value": "true",
        }
    ],
    "combination": 1,
    "entityType": 0,
}


def _progress_status(pages_read: int, total_pages: int) -> tuple[str, float]:
    if total_pages <= 0:
        return ("unread", 0.0)
    percent = round((pages_read / total_pages) * 100, 2)
    if pages_read <= 0:
        return ("unread", 0.0)
    if pages_read >= total_pages:
        return ("completed", 100.0)
    return ("in_progress", percent)


def sync_snapshot() -> dict[str, object]:
    """Validate access and sync a first-pass content snapshot."""
    settings = load_settings()
    bootstrap_database(settings.db_path)
    client = KavitaClient(settings)
    account = client.get_current_user()
    libraries = client.list_libraries()
    series_items = client.list_all_series()
    want_to_read_series = client.list_all_filtered_series(WANT_TO_READ_FILTER)
    want_to_read_ids = {int(item["id"]) for item in want_to_read_series if item.get("id") is not None}

    progress_entries: list[dict[str, object]] = []
    in_progress_series = [
        item for item in series_items
        if isinstance(item.get("id"), int) and isinstance(item.get("pages"), int) and isinstance(item.get("pagesRead"), int)
    ]
    continue_point_hits = 0
    for item in in_progress_series:
        pages = int(item.get("pages") or 0)
        pages_read = int(item.get("pagesRead") or 0)
        status, percent = _progress_status(pages_read, pages)
        current_chapter_id = None
        if status == "in_progress":
            continue_point = client.get_continue_point(int(item["id"]))
            current_chapter_id = continue_point.get("id")
            continue_point_hits += 1
        progress_entries.append(
            {
                "series_id": int(item["id"]),
                "status": status,
                "percent": percent,
                "last_read_at": item.get("latestReadDate"),
                "current_chapter_id": current_chapter_id,
            }
        )

    upsert_libraries(settings.db_path, libraries)
    upsert_series(settings.db_path, series_items)
    replace_want_to_read_flags(settings.db_path, want_to_read_ids)
    upsert_progress_entries(settings.db_path, progress_entries)
    detail = {
        "account": asdict(account),
        "library_count": len(libraries),
        "series_count": len(series_items),
        "want_to_read_count": len(want_to_read_ids),
        "progress_count": len(progress_entries),
        "continue_point_hits": continue_point_hits,
        "db_path": str(settings.db_path),
    }
    log_sync_run(settings.db_path, sync_type="snapshot", status="success", detail=detail)
    return {
        "status": "synced",
        "db_path": str(settings.db_path),
        "account": detail["account"],
        "library_count": detail["library_count"],
        "series_count": detail["series_count"],
        "want_to_read_count": detail["want_to_read_count"],
        "progress_count": detail["progress_count"],
        "message": "Kavita connectivity validated and snapshot stored locally with progress and want-to-read state.",
    }
