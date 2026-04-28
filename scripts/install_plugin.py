#!/usr/bin/env python3
"""Install kavita-recs into ~/.hermes/plugins/."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PLUGIN_DIR = REPO_ROOT / "plugin" / "kavita-recs"
TARGET_PLUGIN_DIR = Path.home() / ".hermes" / "plugins" / "kavita-recs"
TARGET_CONFIG_DIR = Path.home() / ".config" / "kavita-hermes-recs"
TARGET_CONFIG_FILE = TARGET_CONFIG_DIR / "config.env"
SOURCE_ENV_EXAMPLE = REPO_ROOT / ".env.example"


def install_link() -> None:
    TARGET_PLUGIN_DIR.parent.mkdir(parents=True, exist_ok=True)
    if TARGET_PLUGIN_DIR.exists() or TARGET_PLUGIN_DIR.is_symlink():
        TARGET_PLUGIN_DIR.unlink() if TARGET_PLUGIN_DIR.is_symlink() else shutil.rmtree(TARGET_PLUGIN_DIR)
    TARGET_PLUGIN_DIR.symlink_to(SOURCE_PLUGIN_DIR)


def install_copy() -> None:
    TARGET_PLUGIN_DIR.parent.mkdir(parents=True, exist_ok=True)
    if TARGET_PLUGIN_DIR.exists() or TARGET_PLUGIN_DIR.is_symlink():
        TARGET_PLUGIN_DIR.unlink() if TARGET_PLUGIN_DIR.is_symlink() else shutil.rmtree(TARGET_PLUGIN_DIR)
    shutil.copytree(SOURCE_PLUGIN_DIR, TARGET_PLUGIN_DIR)


def maybe_seed_config() -> None:
    TARGET_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not TARGET_CONFIG_FILE.exists():
        shutil.copyfile(SOURCE_ENV_EXAMPLE, TARGET_CONFIG_FILE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install the kavita-recs Hermes plugin.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--link", action="store_true", help="Install as a symlink.")
    mode.add_argument("--copy", action="store_true", help="Install as a copied directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.link:
        install_link()
        maybe_seed_config()
        print(f"Linked plugin to {TARGET_PLUGIN_DIR}")
    elif args.copy:
        install_copy()
        maybe_seed_config()
        print(f"Copied plugin to {TARGET_PLUGIN_DIR}")
    print(f"Config template available at {TARGET_CONFIG_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
