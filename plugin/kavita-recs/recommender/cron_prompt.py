"""Prompt helpers for Hermes cron jobs."""

from __future__ import annotations


def build_daily_recommendation_prompt(time_budget_minutes: int = 45, writeback: bool = False) -> str:
    prompt = (
        f"Run kavita_sync_snapshot first. Then run kavita_recommend_today with "
        f"time_budget_minutes={time_budget_minutes}. "
        "If the recommendation succeeds, summarize the primary pick and backups in under 8 lines."
    )
    if writeback:
        prompt += " After that, run kavita_create_reading_list to write the latest recommendation back to Kavita."
    return prompt
