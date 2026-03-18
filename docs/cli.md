# CLI Tools

Raspi-Sump provides several command line tools installed with the package.

---

## rsump

The main monitoring daemon. This is managed by systemd and does not normally
need to be run manually.

```bash
rsump
```

Reads the `reading_interval` from `raspisump.conf`:

- If `reading_interval = 0` — takes a single reading and exits
- Otherwise — takes readings continuously at the configured interval

The `raspisump` systemd service runs this command automatically.

---

## rsumplog

Query water level readings from the database.

```bash
rsumplog [OPTIONS]
```

### Options

| Option | Description |
|--------|-------------|
| _(none)_ | Show today's readings (default) |
| `--today` | Show today's readings |
| `--date YYYY-MM-DD` | Show readings for a specific date |
| `--last N` | Show the last N readings |
| `--time START END` | Time range within the day (e.g. --time 9:00am 2:30pm). Use with --date or defaults to today. |
| `--cycles` | Show pump cycle count (requires cycle detection enabled) |

### Examples

```bash
# Today's readings
rsumplog

# Readings for a specific date
rsumplog --date 2026-03-15

# Last 10 readings
rsumplog --last 10

# Pump cycles for today (experimental)
rsumplog --cycles

# Pump cycles for a specific date (experimental)
rsumplog --cycles --date 2026-03-15

# Display readings for a specific time period
rsumplog --date 2026-03-15 --time 12:05am 12:16am
```

!!! note "Cycle detection"
    `--cycles` requires `cycle_detection = yes` in the `[experimental]`
    section of `raspisump.conf`. See [Configuration](configuration.md) for details.

---

## rsumpimport

Import historical CSV files from Raspi-Sump 1.x into the SQLite database.

```bash
rsumpimport --dir PATH --unit metric|imperial
rsumpimport --file FILE [FILE ...] --unit metric|imperial
```

### Options

| Option | Description |
|--------|-------------|
| `--dir PATH` | Directory containing `waterlevel-*.csv` files |
| `--file FILE ...` | One or more specific CSV files to import |
| `--unit` | Unit system the CSV data was recorded in (`metric` or `imperial`) |

### Examples

```bash
# Import all CSV files from a directory
rsumpimport --dir ~/raspi-sump-backup/ --unit metric

# Import specific files
rsumpimport --file waterlevel-2025-01-01.csv waterlevel-2025-01-02.csv --unit imperial
```

Duplicate entries are skipped automatically — safe to run more than once.

---

## alerttest

Send a test alert notification using the current configuration.

```bash
alerttest
```

Tests whichever alert type is configured (`alert_type = 1` for email,
`alert_type = 2` for Mastodon). Useful for verifying credentials and
connectivity after initial setup or after changing alert settings.

---

## rsumpsupport

Generate a support information file for bug reports.

```bash
rsumpsupport
```

Dumps system and raspisump environment information to a file in
`/var/lib/raspi-sump/support/`. Attach this file when reporting issues
in the [issue tracker](https://github.com/alaudet/raspi-sump/issues).

!!! note
    The support file does not contain passwords or credentials.
