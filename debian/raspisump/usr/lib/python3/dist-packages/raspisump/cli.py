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


def rsumpchart():
    """Generate a one-time chart of today's sump pit activity."""
    import time
    from raspisump import todaychart

    print("Creating one time chart reading in the charts directory - today.png")
    csv_file = f"/var/lib/raspi-sump/csv/waterlevel-{time.strftime('%Y%m%d')}.csv"
    filename = "/var/lib/raspi-sump/charts/today.png"
    todaychart.graph(csv_file, filename)


def rsumpwebchart():
    """Generate and archive web charts."""
    import time
    from raspisump import webchart

    year = time.strftime("%Y")
    month = time.strftime("%m")
    today = time.strftime("%Y%m%d")
    webchart.create_folders(year, month)
    webchart.create_chart()
    webchart.copy_chart(year, month, today)


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
    logfile = f"{STATE_DIR}/csv/waterlevel-{time.strftime('%Y%m%d')}.csv"
    chart_folder = f"{STATE_DIR}/charts"

    os.makedirs(support_folder, exist_ok=True)

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os_version = get_os_version()
    raspisump_version = get_raspisump_version()
    python_version = get_python_version()
    configs = config_values.configuration()

    raspi_sump_status = run_command(["systemctl", "status", "raspisump"])
    rsumpwebchart_timer_status = run_command(
        ["systemctl", "status", "rsumpwebchart.timer"]
    )
    logs_error_log = run_command(["cat", f"{LOG_DIR}/error_log"])
    logs_info_log = run_command(["cat", f"{LOG_DIR}/info_log"])
    logs_heartbeat_log = run_command(
        ["tail", "-n", "10", f"{LOG_DIR}/heartbeat_log"]
    )
    logs_alert_log = run_command(["tail", "-n", "10", f"{LOG_DIR}/alert_log"])
    waterlevel_csv = run_command(["cat", logfile])
    journal = run_command([
        "journalctl",
        "-u", "raspisump.service",
        "-u", "rsumpwebchart.service",
        "-u", "rsumpwebchart.timer",
        "-b",
    ])
    charts = run_command(["ls", "-alR", chart_folder])
    rsump_service = run_command(["cat", f"{SYSTEMD_DIR}/raspisump.service"])
    rsumpwebchart_service = run_command(
        ["cat", f"{SYSTEMD_DIR}/rsumpwebchart.service"]
    )
    rsumpwebchart_timer = run_command(
        ["cat", f"{SYSTEMD_DIR}/rsumpwebchart.timer"]
    )

    content = f"""\
Date file generated: {current_date}
os version: {os_version}
raspi-sump version: {raspisump_version}
python version on system: {python_version}

Systemctl status for raspisump:
{raspi_sump_status}

Systemctl status for rsumpwebchart.timer:
{rsumpwebchart_timer_status}

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
line_color: {configs["line_color"]}

Logs/error_log content:
{logs_error_log}

Logs/info_log content:
{logs_info_log}

Last 10 lines of heartbeat_log:
{logs_heartbeat_log}

Last 10 lines of alert_log:
{logs_alert_log}

waterlevel csv:
{waterlevel_csv}

journalctl -u raspisump.service -u rsumpwebchart.service -u rsumpwebchart.timer -b:
{journal}

Charts directory:
{charts}

Systemd files:
** Raspi-sump service file:
{rsump_service}
*************************************

** Raspi-sump webchart service file:
{rsumpwebchart_service}
*************************************

** Raspi-sump webchart timer file:
{rsumpwebchart_timer}
*************************************


"""

    with open(support_file_path, "w") as f:
        f.write(content)
    print(f"Support information has been saved to {support_file_path}.")
