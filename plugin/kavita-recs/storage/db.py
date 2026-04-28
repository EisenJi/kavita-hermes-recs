"""SQLite helpers for local recommendation state."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
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
        _apply_migrations(conn)


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"] for row in rows}


def _ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    if column not in _table_columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")


def _apply_migrations(conn: sqlite3.Connection) -> None:
    for column, ddl in [
        ("library_id", "library_id INTEGER"),
        ("library_name", "library_name TEXT"),
        ("pages", "pages INTEGER"),
        ("pages_read", "pages_read INTEGER"),
        ("avg_hours_to_read", "avg_hours_to_read REAL"),
        ("latest_read_date", "latest_read_date TEXT"),
        ("raw_json", "raw_json TEXT"),
    ]:
        _ensure_column(conn, "series_cache", column, ddl)


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat()


def upsert_libraries(db_path: Path, libraries: list[dict[str, object]]) -> None:
    with connect(db_path) as conn:
        now = utc_now_iso()
        conn.executemany(
            """
            INSERT INTO library_cache (library_id, name, library_type, raw_json, updated_at)
            VALUES (:library_id, :name, :library_type, :raw_json, :updated_at)
            ON CONFLICT(library_id) DO UPDATE SET
              name=excluded.name,
              library_type=excluded.library_type,
              raw_json=excluded.raw_json,
              updated_at=excluded.updated_at
            """,
            [
                {
                    "library_id": item["id"],
                    "name": item.get("name") or f"library-{item['id']}",
                    "library_type": str(item.get("type")) if item.get("type") is not None else None,
                    "raw_json": json.dumps(item, ensure_ascii=False),
                    "updated_at": now,
                }
                for item in libraries
            ],
        )


def upsert_series(db_path: Path, series_items: list[dict[str, object]]) -> None:
    with connect(db_path) as conn:
        now = utc_now_iso()
        conn.executemany(
            """
            INSERT INTO series_cache (
              series_id, title, library_id, library_name, summary, format, genres_json, tags_json,
              writers_json, release_year, page_count, read_time_minutes, want_to_read, user_rating,
              external_rating, pages, pages_read, avg_hours_to_read, latest_read_date, raw_json, updated_at
            )
            VALUES (
              :series_id, :title, :library_id, :library_name, :summary, :format, :genres_json, :tags_json,
              :writers_json, :release_year, :page_count, :read_time_minutes, :want_to_read, :user_rating,
              :external_rating, :pages, :pages_read, :avg_hours_to_read, :latest_read_date, :raw_json, :updated_at
            )
            ON CONFLICT(series_id) DO UPDATE SET
              title=excluded.title,
              library_id=excluded.library_id,
              library_name=excluded.library_name,
              summary=excluded.summary,
              format=excluded.format,
              user_rating=excluded.user_rating,
              pages=excluded.pages,
              pages_read=excluded.pages_read,
              avg_hours_to_read=excluded.avg_hours_to_read,
              latest_read_date=excluded.latest_read_date,
              raw_json=excluded.raw_json,
              updated_at=excluded.updated_at
            """,
            [
                {
                    "series_id": item["id"],
                    "title": item.get("name") or f"series-{item['id']}",
                    "library_id": item.get("libraryId"),
                    "library_name": item.get("libraryName"),
                    "summary": None,
                    "format": str(item.get("format")) if item.get("format") is not None else None,
                    "genres_json": "[]",
                    "tags_json": "[]",
                    "writers_json": "[]",
                    "release_year": None,
                    "page_count": item.get("pages"),
                    "read_time_minutes": None,
                    "want_to_read": 0,
                    "user_rating": item.get("userRating"),
                    "external_rating": None,
                    "pages": item.get("pages"),
                    "pages_read": item.get("pagesRead"),
                    "avg_hours_to_read": item.get("avgHoursToRead"),
                    "latest_read_date": item.get("latestReadDate"),
                    "raw_json": json.dumps(item, ensure_ascii=False),
                    "updated_at": now,
                }
                for item in series_items
            ],
        )


def log_sync_run(db_path: Path, sync_type: str, status: str, detail: dict[str, object]) -> None:
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO sync_runs (sync_type, status, detail_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (sync_type, status, json.dumps(detail, ensure_ascii=False), utc_now_iso()),
        )
