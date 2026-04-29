"""Slash command registration for kavita-recs."""

from .config import load_settings
from .recommender.cron_prompt import build_daily_recommendation_prompt
from .recommender.preferences import record_feedback, set_reading_mood
from .recommender.reading_list import create_reading_list_from_latest
from .recommender.sync import sync_snapshot
from .recommender.today import recommend_today


def register_commands(ctx):
    """Register placeholder slash commands."""

    def todayread_command(args):
        settings = load_settings()
        budget = None
        parts = [part for part in str(args or "").split() if part]
        if parts:
            try:
                budget = int(parts[0])
            except ValueError:
                budget = None
        result = recommend_today(
            time_budget_minutes=budget,
            request_text=f"command:/todayread {args}".strip(),
        )
        if result["status"] != "ok":
            return (
                "kavita-recs could not produce a recommendation yet.\n"
                f"- user: {settings.kavita_user_name or 'unset'}\n"
                f"- db: {settings.db_path}\n"
                f"- message: {result['message']}"
            )
        primary = result["primary_pick"]
        lines = [
            "Today's reading pick",
            f"- user: {settings.kavita_user_name or 'unset'}",
            f"- db: {settings.db_path}",
            f"- time budget: {result['time_budget_minutes']} min",
            f"- primary: {primary['title']} ({primary['status']})",
            f"- why: {primary['reason']}",
        ]
        backups = result.get("backup_picks", [])
        if backups:
            lines.append("- backups:")
            for item in backups:
                lines.append(f"  - {item['title']} ({item['status']})")
        return "\n".join(lines)

    ctx.register_command(
        "todayread",
        todayread_command,
        "Generate today's reading recommendation from Kavita.",
    )

    def readingsync_command(args):
        result = sync_snapshot()
        account = result["account"]
        return (
            "kavita-recs connectivity check completed.\n"
            f"- user: {account['username'] or 'unknown'}\n"
            f"- db: {result['db_path']}\n"
            f"- status: {result['status']}\n"
            f"- libraries: {result['library_count']}\n"
            f"- series: {result['series_count']}\n"
            f"- want-to-read: {result['want_to_read_count']}\n"
            f"- progress entries: {result['progress_count']}"
        )

    ctx.register_command(
        "readingsync",
        readingsync_command,
        "Validate Kavita connectivity and prepare local state.",
    )

    def readingfeedback_command(args):
        parts = [part for part in str(args or "").split() if part]
        if len(parts) < 2:
            return "Usage: /readingfeedback <series_id> <liked|disliked|skipped> [reason]"
        try:
            series_id = int(parts[0])
        except ValueError:
            return "series_id must be an integer."
        feedback_type = parts[1]
        reason = " ".join(parts[2:]) if len(parts) > 2 else None
        result = record_feedback(series_id=series_id, feedback_type=feedback_type, reason=reason)
        if result["status"] != "ok":
            return str(result["message"])
        return f"Recorded {result['feedback_type']} for {result['title']} (series_id={result['series_id']})."

    ctx.register_command(
        "readingfeedback",
        readingfeedback_command,
        "Record liked/disliked/skipped feedback for a series.",
    )

    def readingmood_command(args):
        parts = [part for part in str(args or "").split() if part]
        if not parts:
            return "Usage: /readingmood <light|serious|continue|explore> [days]"
        mood = parts[0]
        days = 7
        if len(parts) > 1:
            try:
                days = int(parts[1])
            except ValueError:
                return "days must be an integer."
        result = set_reading_mood(mood=mood, days=days)
        if result["status"] != "ok":
            return str(result["message"])
        return f"Set reading mood to {result['mood']} for {result['days']} days."

    ctx.register_command(
        "readingmood",
        readingmood_command,
        "Set a short-term reading mood preference.",
    )

    def readinglist_command(args):
        title = str(args).strip() or None
        result = create_reading_list_from_latest(title=title)
        if result["status"] != "ok":
            return str(result["message"])
        return (
            f"Created Kavita reading list '{result['title']}' "
            f"(id={result['reading_list_id']}) with {result['item_count']} recommended series."
        )

    ctx.register_command(
        "readinglist",
        readinglist_command,
        "Create a Kavita reading list from the latest recommendation.",
    )

    def readingcron_command(args):
        prompt = build_daily_recommendation_prompt(time_budget_minutes=45, writeback=True)
        return (
            "Suggested Hermes cron setup:\n"
            "python scripts/setup_daily_cron.py --schedule '0 8 * * *' --time-budget 45 --writeback --apply\n"
            "Cron prompt:\n"
            f"{prompt}"
        )

    ctx.register_command(
        "readingcron",
        readingcron_command,
        "Show a suggested Hermes cron setup command for daily recommendations.",
    )
