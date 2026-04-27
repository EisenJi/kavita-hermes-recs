# Architecture

Planned architecture:

- shared `Kavita` content plane
- per-user local `Hermes` plugin
- per-user local SQLite recommendation state
- Hermes cron for daily recommendation generation

High-level model:

```text
Shared Kavita server
  -> library metadata
  -> per-user progress
  -> per-user reading lists

Per-user local machine
  -> Hermes
  -> kavita-recs plugin
  -> local SQLite state
  -> personal recommendation memory
```

Design principles:

- shared library, personal recommendations
- local-first state
- rules first, LLM second
- Hermes-native integration before custom infrastructure
