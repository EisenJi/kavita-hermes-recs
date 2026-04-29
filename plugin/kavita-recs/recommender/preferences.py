"""Feedback recording and preference feature management."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from ..config import load_settings
from ..storage.db import (
    bootstrap_database,
    get_series_title,
    log_feedback,
    upsert_preference_feature,
)


FEEDBACK_WEIGHTS = {
    "liked": 2.0,
    "disliked": -3.0,
    "skipped": -1.0,
}

MOOD_WEIGHTS = {
    "light": 1.5,
    "serious": 1.5,
    "continue": 1.5,
    "explore": 1.5,
}


def _expires_in_days(days: int) -> str:
    return (datetime.now(UTC) + timedelta(days=days)).isoformat()


def record_feedback(series_id: int, feedback_type: str, reason: str | None = None) -> dict[str, object]:
    settings = load_settings()
    bootstrap_database(settings.db_path)

    if feedback_type not in FEEDBACK_WEIGHTS:
        return {
            "status": "error",
            "message": f"Unsupported feedback_type: {feedback_type}",
        }

    title = get_series_title(settings.db_path, series_id)
    if title is None:
        return {
            "status": "error",
            "message": f"Unknown series_id: {series_id}. Run /readingsync first.",
        }

    log_feedback(settings.db_path, series_id, feedback_type, reason)
    upsert_preference_feature(
        settings.db_path,
        feature_key=f"series:{series_id}",
        feature_scope="series_affinity",
        feature_value=title,
        weight=FEEDBACK_WEIGHTS[feedback_type],
        expires_at=None,
    )
    return {
        "status": "ok",
        "series_id": series_id,
        "title": title,
        "feedback_type": feedback_type,
        "weight": FEEDBACK_WEIGHTS[feedback_type],
    }


def set_reading_mood(mood: str, days: int = 7) -> dict[str, object]:
    settings = load_settings()
    bootstrap_database(settings.db_path)

    if mood not in MOOD_WEIGHTS:
        return {
            "status": "error",
            "message": f"Unsupported mood: {mood}",
        }

    expires_at = _expires_in_days(days)
    upsert_preference_feature(
        settings.db_path,
        feature_key="reading_mood",
        feature_scope="short_term",
        feature_value=mood,
        weight=MOOD_WEIGHTS[mood],
        expires_at=expires_at,
    )
    return {
        "status": "ok",
        "mood": mood,
        "days": days,
        "expires_at": expires_at,
    }
