"""Rule-based local recommendation from synced snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any

from ..config import load_settings
from ..storage.db import bootstrap_database, fetch_series_rows, log_recommendation


DEFAULT_PAGE_MINUTES = 1.0


@dataclass(slots=True)
class Candidate:
    series_id: int
    title: str
    library_name: str | None
    status: str
    want_to_read: bool
    pages: int
    pages_read: int
    est_remaining_minutes: int
    percent: float
    score: float
    reason: str


def _estimate_remaining_minutes(row: dict[str, Any]) -> int:
    pages = int(row.get("pages") or 0)
    pages_read = int(row.get("pages_read") or 0)
    remaining_pages = max(0, pages - pages_read)
    avg_hours = row.get("avg_hours_to_read")
    if avg_hours not in (None, 0):
        total_minutes = float(avg_hours) * 60.0
        if pages > 0:
            remaining_ratio = remaining_pages / pages
            return max(1, ceil(total_minutes * remaining_ratio))
    return max(1, ceil(remaining_pages * DEFAULT_PAGE_MINUTES))


def _status_from_row(row: dict[str, Any]) -> str:
    status = row.get("status")
    if isinstance(status, str):
        return status
    pages = int(row.get("pages") or 0)
    pages_read = int(row.get("pages_read") or 0)
    if pages_read <= 0:
        return "unread"
    if pages > 0 and pages_read >= pages:
        return "completed"
    return "in_progress"


def _build_reason(status: str, want_to_read: bool, est_remaining_minutes: int, time_budget_minutes: int) -> str:
    if status == "in_progress" and est_remaining_minutes <= time_budget_minutes:
        return "已经在读，而且今天的时间预算足以明显推进甚至收尾。"
    if status == "in_progress":
        return "已经在读，恢复上下文成本最低，最适合今天继续推进。"
    if want_to_read and est_remaining_minutes <= time_budget_minutes:
        return "它在你的待读列表里，而且今天的时间预算能比较轻松地切入。"
    if want_to_read:
        return "它在你的待读列表里，适合作为今天的新开读选择。"
    if est_remaining_minutes <= time_budget_minutes:
        return "篇幅和预计阅读时间与今天的时间预算比较匹配。"
    return "它在当前快照里属于相对合适的候选。"


def _score_row(row: dict[str, Any], time_budget_minutes: int) -> Candidate:
    series_id = int(row["series_id"])
    title = str(row["title"])
    library_name = row["library_name"]
    pages = int(row.get("pages") or 0)
    pages_read = int(row.get("pages_read") or 0)
    percent = float(row.get("percent") or 0.0)
    status = _status_from_row(row)
    want_to_read = bool(row.get("want_to_read"))
    est_remaining_minutes = _estimate_remaining_minutes(row)

    score = 0.0
    if status == "in_progress":
        score += 40
    elif status == "unread":
        score += 10
    else:
        score -= 100

    if want_to_read:
        score += 12

    if est_remaining_minutes <= time_budget_minutes:
        score += 20
    else:
        overflow = est_remaining_minutes - time_budget_minutes
        score -= min(20, overflow / 10)

    if 0 < percent < 100:
        score += min(20, percent / 5)

    user_rating = row.get("user_rating")
    if user_rating not in (None, 0):
        score += float(user_rating) * 2

    reason = _build_reason(status, want_to_read, est_remaining_minutes, time_budget_minutes)
    return Candidate(
        series_id=series_id,
        title=title,
        library_name=library_name,
        status=status,
        want_to_read=want_to_read,
        pages=pages,
        pages_read=pages_read,
        est_remaining_minutes=est_remaining_minutes,
        percent=percent,
        score=round(score, 2),
        reason=reason,
    )


def recommend_today(
    time_budget_minutes: int | None = None,
    mood: str | None = None,
    request_text: str | None = None,
) -> dict[str, Any]:
    settings = load_settings()
    bootstrap_database(settings.db_path)
    budget = time_budget_minutes or settings.default_time_budget

    rows = fetch_series_rows(settings.db_path)
    candidates = [_score_row(dict(row), budget) for row in rows]
    candidates = [c for c in candidates if c.status != "completed"]
    candidates.sort(key=lambda item: (-item.score, item.est_remaining_minutes, item.title.lower()))

    top = candidates[:3]
    if not top:
        return {
            "status": "empty",
            "message": "本地快照里还没有可推荐的书。请先运行 /readingsync。",
            "time_budget_minutes": budget,
        }

    primary = top[0]
    backups = top[1:]
    result = {
        "status": "ok",
        "time_budget_minutes": budget,
        "mood": mood,
        "primary_pick": {
            "series_id": primary.series_id,
            "title": primary.title,
            "library_name": primary.library_name,
            "status": primary.status,
            "estimated_remaining_minutes": primary.est_remaining_minutes,
            "reason": primary.reason,
            "score": primary.score,
        },
        "backup_picks": [
            {
                "series_id": item.series_id,
                "title": item.title,
                "library_name": item.library_name,
                "status": item.status,
                "estimated_remaining_minutes": item.est_remaining_minutes,
                "reason": item.reason,
                "score": item.score,
            }
            for item in backups
        ],
    }
    log_recommendation(
        settings.db_path,
        request_text=request_text,
        constraints={"time_budget_minutes": budget, "mood": mood},
        candidate_ids=[item.series_id for item in top],
        result=result,
    )
    return result
