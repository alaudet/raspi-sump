"""Retrieve configuration from raspisump.conf and credentials.conf"""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# Credentials should be stored in credentials.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import configparser

config = configparser.RawConfigParser()

config.read([
    "/etc/raspi-sump/raspisump.conf",
    "/etc/raspi-sump/credentials.conf",
])


def configuration():
    """Return a dict of the configuration file"""
    return {
        "critical_water_level": config.getint("pit", "critical_water_level"),
        "pit_depth": config.getint("pit", "pit_depth"),
        "reading_interval": config.getint("pit", "reading_interval"),
        "temperature": config.getint("pit", "temperature"),
        "unit": config.get("pit", "unit"),
        "alert_when": config.get("pit", "alert_when"),
        "trig_pin": config.getint("gpio_pins", "trig_pin"),
        "echo_pin": config.getint("gpio_pins", "echo_pin"),
        "line_color": config.get("charts", "line_color"),
        "email_to": config.get("email", "email_to"),
        "email_from": config.get("email", "email_from"),
        "smtp_authentication": config.getint("email", "smtp_authentication"),
        "smtp_tls": config.getint("email", "smtp_tls"),
        "smtp_ssl": config.getint("email", "smtp_ssl"),
        "smtp_server": config.get("email", "smtp_server"),
        "alert_interval": config.getint("email", "alert_interval"),
        "alert_type": config.getint("email", "alert_type"),
        "heartbeat": config.getint("email", "heartbeat"),
        "heartbeat_interval": config.getint("email", "heartbeat_interval"),
        "username": config.get("credentials", "username"),
        "password": config.get("credentials", "password"),
        "client_id": config.get("credentials", "client_id"),
        "client_secret": config.get("credentials", "client_secret"),
        "access_token": config.get("credentials", "access_token"),
        "api_base_url": config.get("credentials", "api_base_url"),
        "handle": config.get("credentials", "handle"),
    }
