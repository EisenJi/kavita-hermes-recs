# Setup

This document is intentionally practical. It describes the first reproducible local setup path for one user machine.

For Chinese instructions, see:

- `../README.zh-CN.md`

## Prerequisites

You need:

- Python `3.11+`
- a working `Hermes` installation
- access to a `Kavita` server
- a per-user `Kavita` API key

## 1. Clone the repository

```bash
git clone git@github.com:EisenJi/kavita-hermes-recs.git
cd kavita-hermes-recs
```

## 2. Create a user config file

Create the user config directory and copy the example file:

```bash
mkdir -p ~/.config/kavita-hermes-recs
cp .env.example ~/.config/kavita-hermes-recs/config.env
```

Edit at least:

- `KAVITA_BASE_URL`
- `KAVITA_API_KEY`
- `KAVITA_USER_NAME`

The plugin looks for config in this order:

1. `KAVITA_RECS_ENV_FILE`
2. `~/.config/kavita-hermes-recs/config.env`
3. local repo `.env`

## 3. Install the Hermes plugin

The plugin can be linked into `~/.hermes/plugins/` with:

```bash
python scripts/install_plugin.py --link
```

If you prefer a copied install:

```bash
python scripts/install_plugin.py --copy
```

## 4. Bootstrap the local database

```bash
python scripts/bootstrap_db.py
```

This creates the local SQLite database defined by `KAVITA_RECS_DB_PATH`.

## 5. Enable the plugin in Hermes

Enable the plugin by name:

```bash
hermes plugins enable kavita-recs
```

Or use:

```bash
hermes plugins
```

and toggle `kavita-recs` in the interactive UI.

## 6. Verify the scaffold

Start Hermes and try:

```text
/todayread
/readingsync
```

At this stage:

- `/todayread` generates a first local recommendation from the synced snapshot
- `/readingsync` validates Kavita connectivity, boots the local DB, and stores a first-pass snapshot of libraries and series

You can also pass an optional minute budget:

```text
/todayread 45
```

Useful companion commands:

```text
/readingmood light 7
/readingfeedback 123 liked
/readingfeedback 123 disliked too heavy for weekdays
/readinglist
/readingcron
/readingmemory
```

## 7. Set up a daily Hermes cron job

Preview the cron setup:

```bash
python scripts/setup_daily_cron.py
```

Create a daily job at 08:00 that also writes recommendations back to Kavita:

```bash
python scripts/setup_daily_cron.py --schedule "0 8 * * *" --time-budget 45 --writeback --apply
```

This uses Hermes' native cron system and sets the repo as `--workdir`, so the job runs with this repository context.

## 8. Next expected workflow

After the adapter and sync layer are implemented, the normal flow will become:

1. sync Kavita snapshot
2. store local user state
3. generate daily recommendations
4. optionally create a Kavita reading list
5. schedule daily runs with Hermes cron

## Notes

- Each user should use their own `Kavita` account or API key.
- Each user should keep a separate local `.env` and SQLite state file.
- Shared library, personal state: that is the intended deployment model.
