# Architecture

This document explains how `kavita-hermes-recs` is structured and why it is intentionally split across `Kavita`, local SQLite state, and `Hermes`.

## High-Level Model

- shared `Kavita` content plane
- per-user local `Hermes` plugin
- per-user local SQLite recommendation state
- Hermes cron for daily recommendation generation

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

## Design Principles

- shared library, personal recommendations
- local-first state
- rules first, LLM second
- Hermes-native integration before custom infrastructure

## State Layers

The system deliberately separates three state layers.

### 1. Shared Content State

Stored in `Kavita`:

- libraries
- series metadata
- reading progress
- reading lists
- want-to-read markers

This state is authoritative for the shared library.

### 2. Local Recommendation State

Stored in local SQLite:

- snapshot caches
- recommendation logs
- feedback logs
- short-term preference features
- sync history

This state is private to each user machine and should not be pushed into Hermes memory.

### 3. Sparse Memory Candidates

Derived from local state:

- compressed preference summaries
- short, durable user-facing preference hints
- only the highest-value candidate lines

This layer exists because `Hermes memory` is scarce.

## Why Hermes Memory Must Stay Small

`Hermes memory` is not a database. It is prompt budget.

That means:

- raw feedback logs should not go into memory
- transient recommendation weights should not go into memory
- one-off session details should not go into memory

What *can* go into memory:

- stable reading style preferences
- repeated rejection patterns
- durable time-of-day or workload preferences

Example of good memory candidate:

- `User currently prefers lighter weekday reading unless explicitly asking for depth.`

Example of bad memory content:

- raw lists of every disliked title
- every recommendation event
- numerical ranking features

## Recommendation Pipeline

Current pipeline:

1. sync shared content from `Kavita`
2. store a local snapshot in SQLite
3. derive local progress and want-to-read state
4. score candidates with local rules
5. apply preference adjustments from local feedback and short-term mood
6. log recommendation results
7. optionally write the latest picks back to `Kavita` as a `Reading List`

## Why Write Back to Kavita

“Write back to Kavita” means saving the recommendation currently stored in the local log as a `Kavita Reading List`.

It does **not** modify ebook files.

It does:

- make the recommendation visible in the `Kavita` UI
- let the user open recommended books directly from `Kavita`
- keep the shared content platform aware of locally generated picks

## Current Boundaries

What the current implementation does well:

- local-first snapshot sync
- local recommendation iteration
- feedback loop
- cron-friendly automation path

What is still evolving:

- richer metadata enrichment
- stronger scoring logic
- preference summarization into memory drafts
- optional automatic memory update flows
