"""Send Heartbeat alert to test that email notifications are working."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import os
import time
import smtplib
from datetime import datetime, timedelta
from collections import deque
import csv
from raspisump import log, alerts, config_values


user = os.getlogin()

configs = config_values.configuration()


def get_last_alert_time():
    """Retrieve the last alert time string from logfile"""
    heartbeat_log = "/home/" + user + "/raspi-sump/logs/heartbeat_log"
    with open(heartbeat_log, "rt") as f:
        last_row = deque(csv.reader(f), 1)[0]
        return last_row[0]


def heartbeat_email_content():
    """Build the contents of email body which will be sent as an alert"""
    heartbeat_interval_time = configs["heartbeat_interval"]
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    last_alert = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    future_date = last_alert + timedelta(minutes=heartbeat_interval_time + 1)

    weekday = future_date.strftime("%A")[0:3]
    month = future_date.strftime("%B")
    hour = future_date.strftime("%I")
    minute = future_date.strftime("%M")
    am_pm = future_date.strftime("%p").lower()

    time_of_day = alerts.current_time()
    hostname = alerts.host_name()
    subject = "Subject: Raspi-Sump Heartbeat Notification"
    message = "Raspi-Sump Email Notifications Working"

    return "\r\n".join(
        (
            f"From: {configs['email_from']}",
            f"To: {configs['email_to']}",
            f"{subject}",
            "",
            f"{hostname} - {time_of_day} - {message}.",
            f"Next heartbeat: {weekday} {month} {future_date.day} at {hour}:{minute} {am_pm}",
        )
    )


def heartbeat_alerts():
    """Send heartbeat email alert if water level greater
    than critical distance."""
    recipients = configs["email_to"].split(", ")
    email_body = heartbeat_email_content()

    if configs["smtp_ssl"] == 1:
        server = smtplib.SMTP_SSL(configs["smtp_server"])
    elif configs["smtp_tls"] == 1:
        server = smtplib.SMTP(configs["smtp_server"])
        server.starttls()
    else:
        server = smtplib.SMTP(configs["smtp_server"])

    if configs["smtp_authentication"] == 1:
        server.login(configs["username"], configs["password"])

    server.sendmail(configs["email_from"], recipients, email_body)
    server.quit()


def determine_if_heartbeat():
    """Determine if a heartbeat notification is required and if so, send
    the notification."""

    heartbeat_log = "/home/" + user + "/raspi-sump/logs/heartbeat_log"
    if not os.path.isfile(heartbeat_log):
        heartbeat_alerts()
        log.log_event("heartbeat_log", "Heartbeat Email Sent")

    else:
        heartbeat_interval_time = configs["heartbeat_interval"]
        last_email_sent = get_last_alert_time()
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")
        last_heartbeat_time = datetime.strptime(last_email_sent, "%Y-%m-%d %H:%M:%S")
        time_now = datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        delta = time_now - last_heartbeat_time
        minutes_passed = int((delta).total_seconds() / 60)

        if minutes_passed >= heartbeat_interval_time:
            heartbeat_alerts()
            log.log_event("heartbeat_log", "Heartbeat Email Sent")
        else:
            pass
