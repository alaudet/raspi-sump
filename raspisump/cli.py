"""Command line entry points for raspisump."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# Apache-2.0 License -- https://www.linuxnorth.org/raspi-sump/license.html


def rsump():
    """Main raspisump monitoring daemon."""
    import time
    from raspisump import reading, log, config_values

    configs = config_values.configuration()
    reading_interval = configs["reading_interval"]

    def handle_gpio_error():
        error_message = (
            "ERROR -- Cannot access gpio pins. "
            "Make sure the user is part of the gpio group."
        )
        print(error_message)
        log.log_event("error_log", error_message)

    if reading_interval == 0:
        try:
            reading.water_depth()
        except RuntimeError:
            handle_gpio_error()
    else:
        while True:
            try:
                reading.water_depth()
                time.sleep(reading_interval)
            except RuntimeError:
                handle_gpio_error()
                exit(0)


def rsumplog():
    """Query sump pit readings from the SQLite database."""
    import argparse
    from raspisump import log

    parser = argparse.ArgumentParser(
        prog="rsumplog",
        description="Query raspi-sump readings from the database.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--today",
        action="store_true",
        help="Show today's readings (default when no option given)",
    )
    group.add_argument(
        "--date",
        metavar="YYYY-MM-DD",
        help="Show readings for a specific date",
    )
    group.add_argument(
        "--last",
        type=int,
        metavar="N",
        help="Show the last N readings",
    )
    args = parser.parse_args()

    if args.last:
        rows = log.query_readings(last=args.last)
    elif args.date:
        rows = log.query_readings(date=args.date)
    else:
        rows = log.query_readings()

    if not rows:
        print("No readings found.")
        return

    print(f"{'Timestamp':<22} {'Depth':>8}  Unit")
    print("-" * 38)
    for ts, depth, unit in rows:
        print(f"{ts:<22} {depth:>8.2f}  {unit}")
    print(f"\n{len(rows)} reading(s).")


def rsumpimport():
    """Import historical CSV readings into the SQLite database."""
    import argparse
    import glob as globmod
    import os
    from raspisump import log

    parser = argparse.ArgumentParser(
        prog="rsumpimport",
        description="Import raspi-sump 1.x CSV files into the SQLite database.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--dir",
        metavar="PATH",
        help="Directory containing waterlevel-*.csv files",
    )
    source.add_argument(
        "--file",
        nargs="+",
        metavar="FILE",
        help="One or more CSV files to import",
    )
    parser.add_argument(
        "--unit",
        required=True,
        choices=["metric", "imperial"],
        help="Unit system the CSV data was recorded in",
    )
    args = parser.parse_args()

    unit_label = log._UNIT_LABELS[args.unit]

    if args.dir:
        pattern = os.path.join(args.dir, "waterlevel-*.csv")
        paths = sorted(globmod.glob(pattern))
        if not paths:
            print(f"No waterlevel-*.csv files found in {args.dir}")
            return
    else:
        paths = args.file

    print(f"Importing {len(paths)} file(s) as unit '{unit_label}' ...")

    try:
        inserted, skipped, errors = log.import_csv_files(paths, unit_label)
    except OSError as e:
        print(f"Error reading file: {e}")
        return
    except ValueError as e:
        print(f"Error: {e}")
        return
    except Exception as e:
        print(f"Database error — all changes rolled back: {e}")
        return

    for msg in errors:
        print(f"  WARNING: {msg}")

    print(f"\nDone.")
    print(f"  Inserted : {inserted}")
    print(f"  Skipped  : {skipped} (timestamp already in database)")
    if errors:
        print(f"  Warnings : {len(errors)} unparseable line(s) — see above")


def alerttest():
    """Test alert notifications."""
    from raspisump import emailtest

    emailtest.test_notifications()


def rsumpsupport():
    """Dump raspisump environment information to a support file."""
    import os
    import time
    import subprocess
    from datetime import datetime
    from importlib.metadata import version, PackageNotFoundError
    from raspisump import config_values

    LOG_DIR = "/var/log/raspi-sump"
    STATE_DIR = "/var/lib/raspi-sump"
    SYSTEMD_DIR = "/lib/systemd/system"

    def get_os_version():
        with open("/etc/os-release", "r") as file:
            for line in file:
                if line.startswith("VERSION="):
                    return line.strip().split("=")[1].strip('"')

    def get_raspisump_version():
        try:
            return version("raspisump")
        except PackageNotFoundError:
            return "unknown"

    def get_python_version():
        return subprocess.check_output(["python3", "--version"], text=True).strip()

    def run_command(command):
        try:
            return subprocess.check_output(
                command, text=True, stderr=subprocess.PIPE
            ).strip()
        except subprocess.CalledProcessError as e:
            return (
                f"Error executing command: {e.cmd}. "
                f"Return code: {e.returncode}. Output: {e.output}"
            )
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    support_folder = f"{STATE_DIR}/support"
    support_file_path = (
        f"{support_folder}/support-{time.strftime('%Y%m%d_%H%M%S')}.txt"
    )
    os.makedirs(support_folder, exist_ok=True)

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os_version = get_os_version()
    raspisump_version = get_raspisump_version()
    python_version = get_python_version()
    configs = config_values.configuration()

    raspi_sump_status = run_command(["systemctl", "status", "raspisump"])
    rsumpweb_status = run_command(["systemctl", "status", "rsumpweb"])
    logs_error_log = run_command(["cat", f"{LOG_DIR}/error_log"])
    logs_info_log = run_command(["cat", f"{LOG_DIR}/info_log"])
    logs_heartbeat_log = run_command(
        ["tail", "-n", "10", f"{LOG_DIR}/heartbeat_log"]
    )
    logs_alert_log = run_command(["tail", "-n", "10", f"{LOG_DIR}/alert_log"])
    journal = run_command([
        "journalctl",
        "-u", "raspisump.service",
        "-u", "rsumpweb.service",
        "-b",
    ])
    rsump_service = run_command(["cat", f"{SYSTEMD_DIR}/raspisump.service"])
    rsumpweb_service = run_command(["cat", f"{SYSTEMD_DIR}/rsumpweb.service"])

    content = f"""\
Date file generated: {current_date}
os version: {os_version}
raspi-sump version: {raspisump_version}
python version on system: {python_version}

Systemctl status for raspisump:
{raspi_sump_status}

Systemctl status for rsumpweb:
{rsumpweb_status}

Raspi-Sump Variables:
critical_water_level: {configs["critical_water_level"]}
pit_depth: {configs["pit_depth"]}
reading_interval: {configs["reading_interval"]}
temperature: {configs["temperature"]}
trig_pin: {configs["trig_pin"]}
echo_pin: {configs["echo_pin"]}
unit: {configs["unit"]}
alert_type: {configs["alert_type"]}
smtp_tls: {configs["smtp_tls"]}
smtp_ssl: {configs["smtp_ssl"]}
alert_when: {configs["alert_when"]}
alert_interval: {configs["alert_interval"]}
heartbeat: {configs["heartbeat"]}
heartbeat_interval: {configs["heartbeat_interval"]}

Logs/error_log content:
{logs_error_log}

Logs/info_log content:
{logs_info_log}

Last 10 lines of heartbeat_log:
{logs_heartbeat_log}

Last 10 lines of alert_log:
{logs_alert_log}

journalctl -u raspisump.service -u rsumpweb.service -b:
{journal}

Systemd files:
** Raspi-sump service file:
{rsump_service}
*************************************

** Raspi-sump web service file:
{rsumpweb_service}
*************************************


"""

    with open(support_file_path, "w") as f:
        f.write(content)
    print(f"Support information has been saved to {support_file_path}.")
    return support_file_path
