# Usage

This document describes the current day-to-day workflow of `kavita-hermes-recs`.

## Basic Flow

### 1. Sync from Kavita

```text
/readingsync
```

This:

- validates `Kavita` connectivity
- initializes the local SQLite database if needed
- syncs libraries and series snapshots
- derives local progress entries
- syncs `want-to-read`

Run this first on a new machine.

### 2. Ask for a Recommendation

```text
/todayread
/todayread 45
```

This reads the local snapshot and returns:

- one primary pick
- up to two backup picks
- a short reason for the primary pick

The optional integer argument is a time budget in minutes.

### 3. Record Feedback

```text
/readingfeedback 123 liked
/readingfeedback 123 disliked too heavy for weekdays
/readingfeedback 123 skipped
```

This updates:

- `feedback_log`
- `preference_features`

Feedback is local and personal.

### 4. Set a Short-Term Mood

```text
/readingmood light 7
/readingmood continue 3
/readingmood explore 5
```

This creates a temporary preference feature that affects recommendation ranking.

Supported moods:

- `light`
- `serious`
- `continue`
- `explore`

### 5. Write the Latest Recommendation Back to Kavita

```text
/readinglist
/readinglist Weekend Picks
```

This creates a `Kavita Reading List` from the most recent local recommendation.

Use this when you want the picks to appear directly in the `Kavita` UI.

### 6. View Sparse Memory Candidates

```text
/readingmemory
```

This does **not** write to Hermes memory automatically.

It returns a few compressed preference-summary lines that are suitable candidates for future `Hermes` memory updates.

## Daily Automation

### Preview a Cron Job

```bash
python scripts/setup_daily_cron.py
python scripts/setup_daily_cron.py --writeback
python scripts/setup_weekly_summary_cron.py
```

### Create a Cron Job

```bash
python scripts/setup_daily_cron.py --schedule "0 8 * * *" --time-budget 45 --writeback --apply
```

This uses Hermes' native cron feature and sets the repository as the cron workdir.

For weekly preference-summary review:

```bash
python scripts/setup_weekly_summary_cron.py --schedule "0 9 * * 1" --limit 4 --apply
```

This job is intentionally lighter than the daily recommendation job. It does not update Hermes memory automatically. It only emits a compressed weekly review for human inspection or later manual memory updates.

## Practical Advice

- Run `/readingsync` again after adding many books to `Kavita`.
- Use `/readingfeedback` aggressively. This system improves faster from explicit negatives than from silence.
- Keep `/readingmemory` sparse. If a line feels too detailed for a global user profile, it probably belongs in SQLite, not in Hermes memory.
