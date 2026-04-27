# kavita-hermes-recs

[中文](./README.zh-CN.md) | [English](./README.en.md)

Local-first reading recommendation system for `Kavita` powered by `Hermes`.

This repository aims to provide:

- shared `Kavita` library access
- per-user local recommendation state
- per-user `Hermes` integration
- reproducible local setup for family or small-group use

## Status

Scaffold stage. The repository currently contains:

- bilingual README entrypoints
- project layout
- initial architecture docs
- plugin skeleton for Hermes integration

## Core Idea

Use one shared `Kavita` server as the content plane, and run one local `Hermes`-powered recommender per user machine as the decision plane.

```text
Shared Kavita
  -> books, metadata, progress, reading lists

Per-user local Hermes + SQLite
  -> preferences, recommendation history, feedback, daily picks
```

This keeps recommendations personal while keeping the book library shared.

## Repository Layout

```text
plugin/kavita-recs/    Hermes plugin package
docs/                  architecture and setup docs
scripts/               local bootstrap helpers
tests/                 test suite
```

## Next Milestones

1. Implement `Kavita` adapter.
2. Add local SQLite schema and sync job.
3. Add Hermes tools and slash commands.
4. Add daily recommendation flow through Hermes cron.

## License

MIT
