#!/usr/bin/env python3
"""Create the local SQLite database for kavita-recs."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = REPO_ROOT / "plugin" / "kavita-recs"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    config_module = _load_module("kavita_recs_config", PLUGIN_DIR / "config.py")
    db_module = _load_module("kavita_recs_db", PLUGIN_DIR / "storage" / "db.py")
    settings = config_module.load_settings()
    db_module.bootstrap_database(settings.db_path)
    print(f"Initialized database at {settings.db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
