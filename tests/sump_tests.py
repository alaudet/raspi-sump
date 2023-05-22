import os
from nose.tools import *
import raspisump.reading as reading
import raspisump.alerts as alerts
import raspisump.heartbeat as heartbeat

try:
    import ConfigParser as configparser  # Python2
except ImportError:
    import configparser  # Python3

config = configparser.RawConfigParser()
user = os.getlogin()
config.read("/home/" + user + "/raspi-sump/raspisump.conf")

configs = {
    "pit_depth": config.getint("pit", "pit_depth"),
    "unit": config.get("pit", "unit"),
}

try:
    configs["alert_when"] = config.get("pit", "alert_when")
except configparser.NoOptionError:
    configs["alert_when"] = "high"


def test_water_reading():
    """Test that a proper reading is being returned."""
    pit_depth = configs["pit_depth"]
    value = reading.water_reading()
    assert type(value) == float
    assert pit_depth > value


def test_unit_types():
    """Test that a proper unit type is being selected."""
    measurement = alerts.unit_types()
    assert type(measurement) == str
    try:
        assert_equals(measurement, "inches")
    except:
        assert_equals(measurement, "centimeters")


def test_email_content():
    """Test that the right email alert is being returned."""
    water_depth = 35
    email_contents = alerts.email_content(water_depth)
    assert type(email_contents) == str
    beg, sep, end = email_contents.partition("Subject: ")
    assert_equals(beg[0:5], "From:")
    try:
        assert_equals(end[0:9], "Low Water")
    except:
        assert_equals(end[0:9], "Sump Pump")


def test_heartbeat_content():
    """Test that the right email hertbeat is being returned."""
    heartbeat_email_contents = heartbeat.heartbeat_email_content()
    assert type(heartbeat_email_contents) == str
    beg, sep, end = heartbeat_email_contents.partition("Subject: ")
    assert_equals(beg[0:5], "From:")
    assert_equals(end[0:5], "Raspi")


def test_heartbeat_last_row():
    """Test last heartbeat time is correct"""
    heartbeat_log = '/home/' + user + '/raspi-sump/logs/heartbeat_log'
    if not os.path.isfile(heartbeat_log):
        pass
    else:
        last_alert = heartbeat.get_last_alert_time()
        assert type(last_alert) == str
        assert len(last_alert) == 19


def test_hostname_return():
    """Test that hostname is being returned for alert."""
    hostname = alerts.host_name()
    assert type(hostname) == str
