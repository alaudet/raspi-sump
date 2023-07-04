"""Retrieve configuration from raspisump.conf"""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import os
import configparser

config = configparser.RawConfigParser()
user = os.getlogin()

config.read("/home/" + user + "/raspi-sump/raspisump.conf")


def configuration():
    """Return a dict of the configuration file"""

    configs = {
        "critical_water_level": config.getint("pit", "critical_water_level"),
        "pit_depth": config.getint("pit", "pit_depth"),
        "reading_interval": config.getint("pit", "reading_interval"),
        "temperature": config.getint("pit", "temperature"),
        "trig_pin": config.getint("gpio_pins", "trig_pin"),
        "echo_pin": config.getint("gpio_pins", "echo_pin"),
        "unit": config.get("pit", "unit"),
        "email_to": config.get("email", "email_to"),
        "email_from": config.get("email", "email_from"),
        "smtp_authentication": config.getint("email", "smtp_authentication"),
        "smtp_tls": config.getint("email", "smtp_tls"),
        "smtp_server": config.get("email", "smtp_server"),
        "username": config.get("email", "username"),
        "password": config.get("email", "password"),
    }

    # If not in raspisump.conf add to configs dict and provide a default value
    try:
        configs["alert_when"] = config.get("pit", "alert_when")
    except configparser.NoOptionError:
        configs["alert_when"] = "high"

    try:
        configs["alert_interval"] = config.getint("email", "alert_interval")
    except configparser.NoOptionError:
        configs["alert_interval"] = 5

    try:
        configs["smtp_ssl"] = config.getint("email", "smtp_ssl")
    except configparser.NoSectionError:
        configs["smtp_ssl"] = 0

    try:
        configs["heartbeat"] = config.getint("email", "heartbeat")
    except configparser.NoOptionError:
        configs["heartbeat"] = 0

    try:
        configs["heartbeat_interval"] = config.getint("email", "heartbeat_interval")
    except configparser.NoOptionError:
        configs["heartbeat_interval"] = 10080

    try:
        configs["line_color"] = config.get("charts", "line_color")
    except configparser.NoSectionError:
        configs["line_color"] = "FB921D"

    return configs
