# kavita-hermes-recs

[中文](./README.zh-CN.md) | [English](./README.en.md)

Local-first reading recommendation system for `Kavita` powered by `Hermes`.

This repository aims to provide:

- shared `Kavita` library access
- per-user local recommendation state
- per-user `Hermes` integration
- reproducible local setup for family or small-group use

## Status

Early implementation stage. The repository now contains:

- bilingual README entrypoints
- initial architecture and setup docs
- Hermes plugin scaffold
- local config loader
- SQLite bootstrap support
- plugin install helper script

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

## Docs

- [Setup](./docs/setup.md)
- [Architecture](./docs/architecture.md)

## Next Milestones

1. Implement the `Kavita` adapter HTTP layer.
2. Add snapshot sync and local state hydration.
3. Add real recommendation candidate generation.
4. Add daily recommendation flow through Hermes cron.

## License

MIT
