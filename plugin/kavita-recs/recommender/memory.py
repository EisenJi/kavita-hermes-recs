"""Summarize local preference state into sparse Hermes-memory candidates."""

from __future__ import annotations

from collections import Counter

from ..config import load_settings
from ..storage.db import (
    bootstrap_database,
    fetch_active_preference_features,
    fetch_feedback_rows,
)


def summarize_memory_candidates(limit: int = 4) -> dict[str, object]:
    settings = load_settings()
    bootstrap_database(settings.db_path)

    feedback_rows = fetch_feedback_rows(settings.db_path, limit=200)
    feature_rows = fetch_active_preference_features(settings.db_path)

    lines: list[str] = []

    mood_rows = [
        row for row in feature_rows
        if row["feature_scope"] == "short_term" and row["feature_key"] == "reading_mood"
    ]
    if mood_rows:
        mood = str(mood_rows[0]["feature_value"])
        lines.append(f"User currently prefers {mood} reading choices in the short term.")

    affinity_rows = [
        row for row in feature_rows
        if row["feature_scope"] == "series_affinity"
    ]
    liked_titles = [str(row["feature_value"]) for row in affinity_rows if float(row["weight"]) > 0]
    disliked_titles = [str(row["feature_value"]) for row in affinity_rows if float(row["weight"]) < 0]

    if liked_titles:
        lines.append(
            "User has given positive feedback to these recent titles: "
            + ", ".join(liked_titles[:3])
            + "."
        )
    if disliked_titles:
        lines.append(
            "Avoid over-recommending these negatively received titles unless explicitly requested: "
            + ", ".join(disliked_titles[:3])
            + "."
        )

    feedback_counter = Counter(str(row["feedback_type"]) for row in feedback_rows)
    if feedback_counter.get("disliked", 0) >= 2:
        lines.append("User is actively rejecting some recent recommendations, so avoid repeating near-miss picks.")
    if feedback_counter.get("liked", 0) >= 2:
        lines.append("User is responding well to recent recommendation refinement, so keep exploiting confirmed preferences.")

    reason_texts = [
        str(row["feedback_reason"]).strip()
        for row in feedback_rows
        if row["feedback_reason"]
    ]
    if any("heavy" in reason.lower() for reason in reason_texts):
        lines.append("User recently pushed back on overly heavy reading choices, especially for casual sessions.")
    if any("工作日" in reason or "weekday" in reason.lower() for reason in reason_texts):
        lines.append("Weekday recommendations should skew lighter unless the user explicitly asks for depth.")

    deduped: list[str] = []
    seen = set()
    for line in lines:
        key = line.strip()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(key)

    return {
        "status": "ok",
        "candidate_lines": deduped[:limit],
        "source_feedback_count": len(feedback_rows),
        "source_feature_count": len(feature_rows),
        "message": "These lines are suitable candidates for sparse Hermes USER.md memory, not raw state storage.",
    }
