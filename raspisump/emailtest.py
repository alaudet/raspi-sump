"""Send an email on command to test."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import smtplib
from raspisump import alerts, config_values


configs = config_values.configuration()


def test_email_content():
    """Build the contents of test email body."""

    time_of_day = alerts.current_time()
    hostname = alerts.host_name()

    subject = "Subject: Raspi-Sump Email Test"
    message = "Raspi-Sump Test Email"

    return "\r\n".join(
        (
            f"From: {configs['email_from']}",
            f"To: {configs['email_to']}",
            f"{subject}",
            "",
            f"{hostname} - {time_of_day} - {message}.",
        )
    )


def test_email():
    """Send test email only."""
    recipients = configs["email_to"].split(", ")
    email_body = test_email_content()
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
