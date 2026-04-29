"""Write recommendation results back to Kavita as reading lists."""

from __future__ import annotations

from datetime import datetime

from ..adapter.client import KavitaClient
from ..config import load_settings
from ..storage.db import bootstrap_database, fetch_latest_recommendation_result


def _default_title() -> str:
    return datetime.now().strftime("Today Picks - %Y-%m-%d %H:%M")


def create_reading_list_from_latest(title: str | None = None) -> dict[str, object]:
    settings = load_settings()
    bootstrap_database(settings.db_path)

    latest = fetch_latest_recommendation_result(settings.db_path)
    if latest is None:
        return {
            "status": "error",
            "message": "No local recommendation found. Run /todayread first.",
        }

    if latest.get("status") != "ok":
        return {
            "status": "error",
            "message": "Latest recommendation is not usable for reading list creation.",
        }

    series_ids: list[int] = []
    primary = latest.get("primary_pick") or {}
    if isinstance(primary, dict) and primary.get("series_id") is not None:
        series_ids.append(int(primary["series_id"]))
    backups = latest.get("backup_picks") or []
    if isinstance(backups, list):
        for item in backups:
            if isinstance(item, dict) and item.get("series_id") is not None:
                series_ids.append(int(item["series_id"]))

    if not series_ids:
        return {
            "status": "error",
            "message": "Latest recommendation did not contain any series ids.",
        }

    client = KavitaClient(settings)
    list_title = title or _default_title()
    created = client.create_reading_list(list_title)
    reading_list_id = int(created["id"])
    for series_id in series_ids:
        client.add_series_to_reading_list(reading_list_id=reading_list_id, series_id=series_id)

    return {
        "status": "ok",
        "reading_list_id": reading_list_id,
        "title": created.get("title") or list_title,
        "series_ids": series_ids,
        "item_count": len(series_ids),
    }
