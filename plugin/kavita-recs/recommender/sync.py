"""Snapshot sync entrypoints."""

from __future__ import annotations

from dataclasses import asdict

from ..adapter.client import KavitaClient
from ..config import load_settings
from ..storage.db import bootstrap_database, log_sync_run, upsert_libraries, upsert_series


def sync_snapshot() -> dict[str, object]:
    """Validate access and sync a first-pass content snapshot."""
    settings = load_settings()
    bootstrap_database(settings.db_path)
    client = KavitaClient(settings)
    account = client.get_current_user()
    libraries = client.list_libraries()
    series_items = client.list_all_series()
    upsert_libraries(settings.db_path, libraries)
    upsert_series(settings.db_path, series_items)
    detail = {
        "account": asdict(account),
        "library_count": len(libraries),
        "series_count": len(series_items),
        "db_path": str(settings.db_path),
    }
    log_sync_run(settings.db_path, sync_type="snapshot", status="success", detail=detail)
    return {
        "status": "synced",
        "db_path": str(settings.db_path),
        "account": detail["account"],
        "library_count": detail["library_count"],
        "series_count": detail["series_count"],
        "message": "Kavita connectivity validated and first-pass snapshot stored locally.",
    }
