"""Configuration loading for kavita-recs."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_DB_PATH = "~/.local/share/kavita-recs/state.db"
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "kavita-hermes-recs" / "config.env"


def _candidate_env_files() -> list[Path]:
    custom_path = os.getenv("KAVITA_RECS_ENV_FILE")
    candidates: list[Path] = []
    if custom_path:
        candidates.append(Path(os.path.expanduser(custom_path)))
    candidates.append(DEFAULT_CONFIG_PATH)
    candidates.append(Path.cwd() / ".env")
    return candidates


def _load_env_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def _load_dotenv() -> None:
    """Load simple KEY=VALUE pairs from the preferred config path."""
    for candidate in _candidate_env_files():
        if candidate.is_file():
            _load_env_file(candidate)
            return


@dataclass(slots=True)
class Settings:
    kavita_base_url: str | None
    kavita_api_key: str | None
    kavita_user_name: str | None
    kavita_timeout_seconds: int
    db_path: Path
    default_time_budget: int
    default_results: int


def load_settings() -> Settings:
    """Load plugin settings from environment variables and .env."""
    _load_dotenv()
    db_path = Path(os.path.expanduser(os.getenv("KAVITA_RECS_DB_PATH", DEFAULT_DB_PATH)))
    return Settings(
        kavita_base_url=os.getenv("KAVITA_BASE_URL"),
        kavita_api_key=os.getenv("KAVITA_API_KEY"),
        kavita_user_name=os.getenv("KAVITA_USER_NAME"),
        kavita_timeout_seconds=int(os.getenv("KAVITA_TIMEOUT_SECONDS", "20")),
        db_path=db_path,
        default_time_budget=int(os.getenv("KAVITA_RECS_DEFAULT_TIME_BUDGET", "45")),
        default_results=int(os.getenv("KAVITA_RECS_DEFAULT_RESULTS", "3")),
    )
