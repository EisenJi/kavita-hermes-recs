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


def replace_want_to_read_flags(db_path: Path, series_ids: set[int]) -> None:
    with connect(db_path) as conn:
        conn.execute("UPDATE series_cache SET want_to_read = 0")
        if series_ids:
            conn.executemany(
                "UPDATE series_cache SET want_to_read = 1 WHERE series_id = ?",
                [(series_id,) for series_id in series_ids],
            )


def upsert_progress_entries(db_path: Path, progress_items: list[dict[str, object]]) -> None:
    with connect(db_path) as conn:
        now = utc_now_iso()
        conn.executemany(
            """
            INSERT INTO progress_cache (
              series_id, status, percent, last_read_at, current_chapter_id, updated_at
            )
            VALUES (
              :series_id, :status, :percent, :last_read_at, :current_chapter_id, :updated_at
            )
            ON CONFLICT(series_id) DO UPDATE SET
              status=excluded.status,
              percent=excluded.percent,
              last_read_at=excluded.last_read_at,
              current_chapter_id=excluded.current_chapter_id,
              updated_at=excluded.updated_at
            """,
            [
                {
                    "series_id": item["series_id"],
                    "status": item["status"],
                    "percent": item["percent"],
                    "last_read_at": item["last_read_at"],
                    "current_chapter_id": item["current_chapter_id"],
                    "updated_at": now,
                }
                for item in progress_items
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


def fetch_series_rows(db_path: Path) -> list[sqlite3.Row]:
    with connect(db_path) as conn:
        return conn.execute(
            """
            SELECT
              s.series_id,
              s.title,
              s.library_id,
              s.library_name,
              s.format,
              s.want_to_read,
              s.user_rating,
              s.pages,
              s.pages_read,
              s.avg_hours_to_read,
              s.latest_read_date,
              p.status,
              p.percent,
              p.current_chapter_id
            FROM series_cache s
            LEFT JOIN progress_cache p ON p.series_id = s.series_id
            ORDER BY s.title COLLATE NOCASE ASC
            """
        ).fetchall()


def log_recommendation(
    db_path: Path,
    request_text: str | None,
    constraints: dict[str, object],
    candidate_ids: list[int],
    result: dict[str, object],
) -> None:
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO recommendation_log (
              requested_at, request_text, constraints_json, candidate_ids_json, result_json, accepted
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now_iso(),
                request_text,
                json.dumps(constraints, ensure_ascii=False),
                json.dumps(candidate_ids, ensure_ascii=False),
                json.dumps(result, ensure_ascii=False),
                None,
            ),
        )


def fetch_latest_recommendation_result(db_path: Path) -> dict[str, object] | None:
    with connect(db_path) as conn:
        row = conn.execute(
            """
            SELECT result_json
            FROM recommendation_log
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
        if row is None or not row["result_json"]:
            return None
        return json.loads(str(row["result_json"]))


def get_series_title(db_path: Path, series_id: int) -> str | None:
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT title FROM series_cache WHERE series_id = ?",
            (series_id,),
        ).fetchone()
        if row is None:
            return None
        return str(row["title"])


def log_feedback(db_path: Path, series_id: int, feedback_type: str, feedback_reason: str | None) -> None:
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO feedback_log (series_id, feedback_type, feedback_reason, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (series_id, feedback_type, feedback_reason, utc_now_iso()),
        )


def upsert_preference_feature(
    db_path: Path,
    feature_key: str,
    feature_scope: str,
    feature_value: str,
    weight: float,
    expires_at: str | None = None,
) -> None:
    with connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO preference_features (
              feature_key, feature_scope, feature_value, weight, updated_at, expires_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(feature_key, feature_scope) DO UPDATE SET
              feature_value=excluded.feature_value,
              weight=excluded.weight,
              updated_at=excluded.updated_at,
              expires_at=excluded.expires_at
            """,
            (feature_key, feature_scope, feature_value, weight, utc_now_iso(), expires_at),
        )


def fetch_active_preference_features(db_path: Path) -> list[sqlite3.Row]:
    with connect(db_path) as conn:
        return conn.execute(
            """
            SELECT feature_key, feature_scope, feature_value, weight, expires_at, updated_at
            FROM preference_features
            WHERE expires_at IS NULL OR expires_at > ?
            """,
            (utc_now_iso(),),
        ).fetchall()
