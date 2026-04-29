# kavita-hermes-recs

[中文](./README.zh-CN.md) | [English](./README.en.md)

`kavita-hermes-recs` is a local-first reading recommendation system for `Kavita`, with `Hermes` as the interaction and automation layer.

It is designed for this deployment model:

- one shared `Kavita` server
- one local `Hermes` instance per user
- one local SQLite recommendation state per user

This makes it suitable for family or small-group use:

- the library is shared
- recommendations remain personal
- feedback does not pollute other users' preferences

## What It Does

Current repository capabilities:

- sync libraries and series snapshots from `Kavita`
- infer local progress state from synced metadata
- track `want-to-read` and continue points
- generate rule-based daily recommendations locally
- record feedback and short-term reading mood
- summarize sparse preference candidates suitable for `Hermes` memory
- write the latest recommendation back to `Kavita` as a `Reading List`
- generate a native `Hermes cron` setup command for daily automation

## Why This Architecture

The system is intentionally split into two planes:

- shared content plane: `Kavita`
  - books, metadata, reading progress, reading lists
- personal decision plane: local `Hermes + SQLite`
  - recommendation history, feedback, temporary preference state, daily picks

Why this matters:

- `Kavita` already solves shared library management well
- recommendation state should remain personal and local
- `Hermes memory` is a scarce resource and should only store compressed, long-lived summaries
- raw recommendation logs and weights belong in SQLite, not in `USER.md`

## Current User Flow

1. Run `/readingsync` to pull a local snapshot from `Kavita`.
2. Run `/todayread` to generate a local recommendation.
3. Run `/readingfeedback` and `/readingmood` to refine future recommendations.
4. Run `/readinglist` if you want to save the latest recommendation back into `Kavita`.
5. Run `/readingcron` or `python scripts/setup_daily_cron.py` if you want daily automation.
6. Run `/readingmemory` to get a sparse summary of preference lines that are safe candidates for future `Hermes` memory updates.

## Commands

Current Hermes plugin commands:

- `/readingsync`
- `/todayread [minutes]`
- `/readingfeedback <series_id> <liked|disliked|skipped> [reason]`
- `/readingmood <light|serious|continue|explore> [days]`
- `/readinglist [title]`
- `/readingcron`
- `/readingmemory`

## Quick Start

```bash
git clone git@github.com:EisenJi/kavita-hermes-recs.git
cd kavita-hermes-recs

mkdir -p ~/.config/kavita-hermes-recs
cp .env.example ~/.config/kavita-hermes-recs/config.env

python scripts/install_plugin.py --link
python scripts/bootstrap_db.py

hermes plugins enable kavita-recs
```

Then in Hermes:

```text
/readingsync
/todayread 45
```

## Documentation

- [Setup](./docs/setup.md)
- [Usage](./docs/usage.md)
- [Architecture](./docs/architecture.md)

## Repository Layout

```text
plugin/kavita-recs/    Hermes plugin package
docs/                  setup, usage, architecture
scripts/               bootstrap and cron helpers
tests/                 test suite
```

## Status

This project is still in active build-out. The current implementation is already usable as a local prototype, but the ranking logic and metadata enrichment are still evolving.

## License

MIT
