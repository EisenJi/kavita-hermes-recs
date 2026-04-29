#!/usr/bin/env python3
"""Create a Hermes cron job for daily Kavita recommendations."""

from __future__ import annotations

import argparse
import shlex
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
import sys


def _load_prompt_builder():
    import importlib.util

    source = REPO_ROOT / "plugin" / "kavita-recs" / "recommender" / "cron_prompt.py"
    spec = importlib.util.spec_from_file_location("kavita_recs_cron_prompt", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load prompt builder from {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["kavita_recs_cron_prompt"] = module
    spec.loader.exec_module(module)
    return module.build_daily_recommendation_prompt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a Hermes cron job for daily Kavita recommendations.")
    parser.add_argument("--schedule", default="0 8 * * *", help="Cron schedule expression.")
    parser.add_argument("--time-budget", type=int, default=45, help="Reading time budget in minutes.")
    parser.add_argument("--name", default="Kavita Daily Recommendation", help="Cron job name.")
    parser.add_argument("--deliver", default="local", help="Hermes delivery target. Defaults to local.")
    parser.add_argument("--writeback", action="store_true", help="Also write the latest recommendation back to Kavita as a reading list.")
    parser.add_argument("--apply", action="store_true", help="Actually create the Hermes cron job.")
    return parser.parse_args()


def build_command(schedule: str, prompt: str, name: str, deliver: str) -> list[str]:
    return [
        "hermes",
        "cron",
        "create",
        schedule,
        prompt,
        "--name",
        name,
        "--deliver",
        deliver,
        "--workdir",
        str(REPO_ROOT),
    ]


def main() -> int:
    args = parse_args()
    hermes_bin = shutil.which("hermes")
    if hermes_bin is None:
        print("Hermes CLI was not found in PATH.")
        return 1

    build_prompt = _load_prompt_builder()
    prompt = build_prompt(time_budget_minutes=args.time_budget, writeback=args.writeback)
    command = build_command(args.schedule, prompt, args.name, args.deliver)

    print("Cron prompt:")
    print(prompt)
    print()
    print("Command:")
    print(shlex.join(command))

    if not args.apply:
        print()
        print("Dry run only. Re-run with --apply to create the Hermes cron job.")
        return 0

    completed = subprocess.run(command, cwd=REPO_ROOT, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
