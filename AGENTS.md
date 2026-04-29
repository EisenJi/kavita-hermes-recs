# AGENTS.md

## Project Purpose

`kavita-hermes-recs` is a local-first reading recommendation system for shared `Kavita` libraries with per-user local `Hermes` integration.

Core deployment model:

- one shared `Kavita` server
- one local recommender state per user machine
- one local `Hermes` instance per user

## Current Priorities

Work in this order unless the user explicitly redirects:

1. keep the project usable for real-world daily use
2. preserve clean docs and reproducible setup
3. gather real user feedback before expanding complexity
4. improve ranking logic only after usage feedback justifies it
5. keep Hermes memory sparse and summary-oriented

## Commit Convention

All commits should use a clear conventional-style prefix.

Preferred prefixes:

- `feat:` new functionality
- `fix:` bug fix
- `chore:` maintenance, refactor, tooling, docs plumbing
- `docs:` documentation-only changes
- `test:` tests only

Examples:

- `feat: add Kavita connectivity validation`
- `fix: load config from user config directory first`
- `docs: expand bilingual setup instructions`
- `chore: bootstrap local sqlite schema`

Do not create vague commit messages like:

- `update`
- `changes`
- `init`

## Documentation Rules

- Keep user-facing repository docs available in both Chinese and English when practical.
- `README.md` is the language switchboard.
- Add Chinese docs alongside English docs for installation and usage flows when those flows change materially.

## Config and State Rules

- User config should prefer `~/.config/kavita-hermes-recs/config.env`
- Local state should remain per-user and local-first
- Do not hardcode machine-specific absolute paths into repository files
- Do not store secrets in the repository

## Integration Rules

- Prefer Hermes-native integration patterns before inventing parallel infrastructure
- Use Hermes plugin capabilities first
- Use Hermes cron for scheduled recommendation workflows
- Use Hermes memory only for compact long-lived summaries, not raw recommendation logs

## Implementation Rules

- Prefer small, verifiable increments
- Validate bootstrap and local scripts after changing them
- Keep recommendation logic explainable; do not hide hard constraints inside prompts
