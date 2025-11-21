"""Send an email on command to test."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import smtplib
from mastodon import Mastodon
from raspisump import log, alerts, config_values


configs = config_values.configuration()


def test_notification_content():
    """Build the contents of test message body."""

    time_of_day = alerts.current_time()
    hostname = alerts.host_name()

    subject = "Subject: Raspi-Sump Email Test"
    message = "Raspi-Sump Test Notification"

    if configs["alert_type"] == 1:
        return "\r\n".join(
            (
                f"From: {configs['email_from']}",
                f"To: {configs['email_to']}",
                f"{subject}",
                "",
                f"{hostname} - {time_of_day} - {message}.",
            )
        )

    if configs["alert_type"] == 2:
        return "\r\n".join((f"{hostname} - {time_of_day} - {message}.",))


def test_email():
    """Send test email only."""
    recipients = configs["email_to"].split(", ")
    email_body = test_notification_content()
    try:
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

    except Exception as e:
        log.log_event("error_log", f"{e}")


def test_mastodon():
    """Send a mastodon test toot"""
    recipient = configs["handle"]
    mastodon_body = test_notification_content()
    toot = f"{recipient} {mastodon_body}"

    mastodon = Mastodon(
        client_id=configs["client_id"],
        client_secret=configs["client_secret"],
        access_token=configs["access_token"],
        api_base_url=configs["api_base_url"],
    )

    try:
        mastodon.status_post(
            status=toot,
            visibility="direct",
        )
    except Exception as e:
        log.log_event("error_log", f"{e}")


def test_notifications():
    """Send an email or mastodon test alert based on user notification preference."""
    if configs["alert_type"] == 1:
        test_email()
    elif configs["alert_type"] == 2:
        test_mastodon()
