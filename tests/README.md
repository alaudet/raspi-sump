# Running Tests

## Install pytest system wide

```sh
sudo apt install python3-pytest
```

All GPIO and hardware dependencies are mocked — tests run on any machine without a Raspberry Pi or sensor attached.

Flask web tests are skipped automatically if Flask is not installed on the development machine. Install the `.deb` package on a Pi to validate web functionality.

## Commands

Run all tests:
```sh
pytest tests/
```

Run a single test file:
```sh
pytest tests/test_sump.py
```

Run a single test:
```sh
pytest tests/test_sump.py::TestRaspisump::test_config_dict
```

## Test files

| File | What it covers |
|---|---|
| `test_config_values.py` | Config file parsing and value validation |
| `test_import_csv.py` | CSV import into SQLite |
| `test_logging.py` | SQLite logging, WAL mode, file permissions |
| `test_rsumplog.py` | `rsumplog` CLI — `--today`, `--date`, `--last` |
| `test_sump.py` | Core raspisump config values and reading logic |
| `test_web_admin.py` | Admin system status page and service control |
| `test_web_backup.py` | Backup/export zip download |
| `test_web_config.py` | Configuration editor — load, validate, write |
| `test_web_csvdata.py` | CSV import and export via web |
| `test_web_history.py` | Historical readings — single day, multi-day, custom range |
| `test_web_home.py` | Homepage stat cards and chart container |
| `test_web_stats.py` | Day statistics aggregation |
| `test_web_support.py` | Support file download and alert test |
| `test_web_system.py` | Service status helpers and journal log fetching |

## Contributing

All tests must pass before submitting a pull request. New functionality should include a corresponding test.
