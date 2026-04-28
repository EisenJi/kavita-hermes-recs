"""Slash command registration for kavita-recs."""

from .config import load_settings
from .recommender.sync import sync_snapshot


def register_commands(ctx):
    """Register placeholder slash commands."""

    def todayread_command(args):
        settings = load_settings()
        return (
            "kavita-recs scaffold is installed.\n"
            f"- user: {settings.kavita_user_name or 'unset'}\n"
            f"- db: {settings.db_path}\n"
            "- `/todayread` recommendation flow is not implemented yet."
        )

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
            f"- status: {result['status']}"
        )

    ctx.register_command(
        "readingsync",
        readingsync_command,
        "Validate Kavita connectivity and prepare local state.",
    )
