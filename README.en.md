# kavita-hermes-recs

[中文](./README.zh-CN.md) | [English](./README.en.md)

`kavita-hermes-recs` is a local-first reading recommendation system for `Kavita`, using `Hermes` as the interaction and automation layer.

It targets this deployment model:

- one shared `Kavita` server
- one local `Hermes` instance per user
- one local SQLite recommendation state per user

This is useful for families or small groups because:

- the library is shared
- recommendations remain personal
- one user's feedback does not corrupt another user's preference state

## What It Can Do Today

The repository currently supports:

- syncing libraries and series snapshots from `Kavita`
- deriving local reading progress state from synced metadata
- tracking `want-to-read` and continue points
- generating rule-based daily recommendations locally
- recording feedback and short-term reading mood
- summarizing sparse preference candidates suitable for `Hermes` memory
- writing the latest recommendation back to `Kavita` as a `Reading List`
- generating native `Hermes cron` setup commands for daily automation

## Why It Is Designed This Way

The system is intentionally split into two planes:

- shared content plane: `Kavita`
  - books, metadata, reading progress, reading lists
- personal decision plane: local `Hermes + SQLite`
  - recommendation history, feedback, short-term preference state, daily picks

Why this matters:

- `Kavita` is already good at shared library management
- recommendation state should remain private and local
- `Hermes memory` is scarce and should only hold compressed, long-lived preference summaries
- raw logs, ranking weights, and transient state belong in SQLite, not `USER.md`

## Current Workflow

1. Run `/readingsync` to pull a local snapshot from `Kavita`.
2. Run `/todayread` to generate a local recommendation.
3. Run `/readingfeedback` and `/readingmood` to refine future recommendations.
4. Run `/readinglist` if you want the latest recommendation to appear in `Kavita`.
5. Run `/readingcron` or `python scripts/setup_daily_cron.py` if you want daily automation.
6. Run `/readingmemory` to get sparse preference-summary lines that are safe candidates for future `Hermes` memory updates.

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

The project is still under active development. It is already usable as a local prototype, but ranking logic and metadata enrichment are still evolving.

## License

MIT
