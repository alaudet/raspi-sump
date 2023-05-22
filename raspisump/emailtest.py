"""Send an email on command to test."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import os
import smtplib
import configparser
from raspisump import alerts


config = configparser.RawConfigParser()
user = os.getlogin()
config.read("/home/" + user + "/raspi-sump/raspisump.conf")

configs = {
    "email_to": config.get("email", "email_to"),
    "email_from": config.get("email", "email_from"),
    "smtp_authentication": config.getint("email", "smtp_authentication"),
    "smtp_tls": config.getint("email", "smtp_tls"),
    "smtp_server": config.get("email", "smtp_server"),
    "username": config.get("email", "username"),
    "password": config.get("email", "password"),
}


def test_email_content():

    """Build the contents of test email body."""

    time_of_day = alerts.current_time()
    hostname = alerts.host_name()

    subject = "Subject: Raspi-Sump Email Test"
    message = "Raspi-Sump Test Email"

    return "\r\n".join(
        (
            "From: {}".format(configs["email_from"]),
            "To: {}".format(configs["email_to"]),
            "{}".format(subject),
            "",
            "{} - {} - {}.".format(hostname, time_of_day, message),
        )
    )


def test_email():
    """Send test email only."""
    recipients = configs["email_to"].split(", ")
    email_body = test_email_content()
    server = smtplib.SMTP(configs["smtp_server"])

    # Check if smtp server uses TLS
    if configs["smtp_tls"] == 1:
        server.starttls()
    else:
        pass
    # Check if smtp server uses authentication
    if configs["smtp_authentication"] == 1:
        username = configs["username"]
        password = configs["password"]
        server.login(username, password)
    else:
        pass

    server.sendmail(configs["email_from"], recipients, email_body)
    server.quit()
