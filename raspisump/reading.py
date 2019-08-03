""" Module to take a water_level reading."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

try:
    import ConfigParser as configparser  # Python2
except ImportError:
    import configparser  # Python3
from hcsr04sensor import sensor
from raspisump import log, alerts, heartbeat

config = configparser.RawConfigParser()
config.read("/home/pi/raspi-sump/raspisump.conf")

configs = {
    "critical_water_level": config.getint("pit", "critical_water_level"),
    "pit_depth": config.getint("pit", "pit_depth"),
    "temperature": config.getint("pit", "temperature"),
    "trig_pin": config.getint("gpio_pins", "trig_pin"),
    "echo_pin": config.getint("gpio_pins", "echo_pin"),
    "unit": config.get("pit", "unit"),
}


def initiate_heartbeat():
    """Initiate the heartbeat email process if needed"""
    if configs["heartbeat"] == 1:
        heartbeat.determine_if_heartbeat()
    else:
        pass


def water_reading():
    """Initiate a water level reading."""
    pit_depth = configs["pit_depth"]
    trig_pin = configs["trig_pin"]
    echo_pin = configs["echo_pin"]
    temperature = configs["temperature"]
    unit = configs["unit"]

    value = sensor.Measurement(trig_pin, echo_pin, temperature, unit)

    try:
        raw_distance = value.raw_distance(sample_wait=0.3)
    except SystemError:
        log.log_errors(
            "**ERROR - Signal not received. Possible cable or sensor problem."
        )
        exit(0)

    return round(value.depth(raw_distance, pit_depth), 1)


def water_depth():
    """Determine the depth of the water, log result and generate alert
    if needed.
    """

    critical_water_level = configs["critical_water_level"]
    water_depth = water_reading()

    if water_depth < 0.0:
        water_depth = 0.0
    log.log_reading(water_depth)

    if water_depth > critical_water_level and configs["alert_when"] == "high":
        alerts.determine_if_alert(water_depth)
    elif water_depth < critical_water_level and configs["alert_when"] == "low":
        alerts.determine_if_alert(water_depth)
    else:
        pass

    initiate_heartbeat()
