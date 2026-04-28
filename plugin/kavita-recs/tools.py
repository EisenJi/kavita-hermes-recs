"""Tool registration for kavita-recs."""

from .config import load_settings
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
        return {
            "status": "scaffold",
            "message": "kavita_recommend_today is not implemented yet.",
            "configured_user": settings.kavita_user_name,
            "db_path": str(settings.db_path),
            "received": params,
        }

    ctx.register_tool("kavita_recommend_today", schema, handle_recommend_today)
