"""SQLite helpers for local recommendation state."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def schema_path() -> Path:
    return Path(__file__).with_name("schema.sql")


def ensure_parent_dir(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)


def connect(db_path: Path) -> sqlite3.Connection:
    ensure_parent_dir(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def bootstrap_database(db_path: Path) -> None:
    with connect(db_path) as conn:
        conn.executescript(schema_path().read_text(encoding="utf-8"))
