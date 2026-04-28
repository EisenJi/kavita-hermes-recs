"""Slash command registration for kavita-recs."""

from .config import load_settings
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
