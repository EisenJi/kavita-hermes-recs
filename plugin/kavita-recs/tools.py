"""Tool registration for kavita-recs."""

from .config import load_settings
from .recommender.preferences import record_feedback, set_reading_mood
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

    feedback_schema = {
        "name": "kavita_record_feedback",
        "description": "Record user feedback for a recommended or read series.",
        "parameters": {
            "type": "object",
            "properties": {
                "series_id": {"type": "integer"},
                "feedback_type": {
                    "type": "string",
                    "description": "One of liked, disliked, skipped.",
                },
                "reason": {"type": "string"},
            },
            "required": ["series_id", "feedback_type"],
        },
    }

    def handle_feedback(params):
        return record_feedback(
            series_id=int(params["series_id"]),
            feedback_type=str(params["feedback_type"]),
            reason=params.get("reason"),
        )

    ctx.register_tool("kavita_record_feedback", feedback_schema, handle_feedback)

    mood_schema = {
        "name": "kavita_set_reading_mood",
        "description": "Set a short-term reading mood preference.",
        "parameters": {
            "type": "object",
            "properties": {
                "mood": {
                    "type": "string",
                    "description": "One of light, serious, continue, explore.",
                },
                "days": {"type": "integer"},
            },
            "required": ["mood"],
        },
    }

    def handle_mood(params):
        return set_reading_mood(
            mood=str(params["mood"]),
            days=int(params.get("days", 7)),
        )

    ctx.register_tool("kavita_set_reading_mood", mood_schema, handle_mood)
