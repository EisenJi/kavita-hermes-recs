"""Tool registration for kavita-recs."""

from .config import load_settings
from .recommender.today import recommend_today
from .recommender.sync import sync_snapshot
from .storage.db import bootstrap_database


def register_tools(ctx):
    """Register placeholder tools."""

    schema = {
        "name": "kavita_recommend_today",
        "description": "Return today's reading recommendation from Kavita.",
        "parameters": {
            "type": "object",
            "properties": {
                "time_budget_minutes": {
                    "type": "integer",
                    "description": "Optional reading time budget in minutes.",
                },
                "mood": {
                    "type": "string",
                    "description": "Optional reading mood such as light or serious.",
                },
            },
        },
    }

    def handle_recommend_today(params):
        settings = load_settings()
        bootstrap_database(settings.db_path)
        return recommend_today(
            time_budget_minutes=params.get("time_budget_minutes"),
            mood=params.get("mood"),
            request_text="tool:kavita_recommend_today",
        )

    ctx.register_tool("kavita_recommend_today", schema, handle_recommend_today)

    sync_schema = {
        "name": "kavita_sync_snapshot",
        "description": "Validate Kavita connectivity and prepare the local state database.",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    }

    def handle_sync_snapshot(params):
        return sync_snapshot()

    ctx.register_tool("kavita_sync_snapshot", sync_schema, handle_sync_snapshot)
