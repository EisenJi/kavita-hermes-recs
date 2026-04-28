# kavita-hermes-recs

[中文](./README.zh-CN.md) | [English](./README.en.md)

A local-first reading recommendation system for `Kavita` with `Hermes` as the interaction layer.

The project is designed for:

- one shared `Kavita` library
- one local recommender per user machine
- one local `Hermes` instance per user
- reproducible setup for family or small-group use

## Current Status

This repository is in early implementation stage and currently includes:

- bilingual README entrypoints
- first-pass architecture and setup docs
- a Hermes plugin scaffold
- local config loading
- SQLite bootstrap support
- a plugin install helper script

## Core Model

Split the system into two planes:

- shared content plane: `Kavita`
  - books, metadata, reading progress, reading lists
- personal decision plane: per-user local `Hermes + SQLite`
  - preferences, feedback, recommendation history, daily picks

```text
Shared Kavita
  -> books, metadata, progress, reading lists

Per-user local Hermes + SQLite
  -> preferences, feedback, recommendation history, daily picks
```

This gives you:

- shared library management
- personal recommendations
- no cross-user preference contamination
- straightforward open-source reproducibility

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
4. Wire daily recommendations through Hermes cron.

## License

MIT
