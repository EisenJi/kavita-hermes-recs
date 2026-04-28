"""Snapshot sync entrypoints."""

from __future__ import annotations

from dataclasses import asdict

from ..adapter.client import KavitaClient
from ..config import load_settings
from ..storage.db import bootstrap_database


def sync_snapshot() -> dict[str, object]:
    """Validate access and prepare local state for future sync work."""
    settings = load_settings()
    bootstrap_database(settings.db_path)
    client = KavitaClient(settings)
    account = client.get_current_user()
    return {
        "status": "validated",
        "db_path": str(settings.db_path),
        "account": asdict(account),
        "message": "Kavita connectivity validated. Snapshot sync implementation is next.",
    }
