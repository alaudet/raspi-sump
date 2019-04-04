'''Log waterlevel readings, restarts and alerts.'''

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

import time


def log_reading(water_depth):
    '''Log time and water depth reading.'''
    time_of_reading = time.strftime("%H:%M:%S,")
    filename = "/home/pi/raspi-sump/csv/waterlevel-{}.csv".format(
        time.strftime("%Y%m%d")
    )
    csv_file = open(filename, 'a')
    csv_file.write(time_of_reading),
    csv_file.write(str(water_depth)),
    csv_file.write("\n")
    csv_file.close()


def log_restarts(reason):
    '''Log all process restarts'''
    logfile = open("/home/pi/raspi-sump/logs/process_log", 'a')
    logfile.write(time.strftime("%Y-%m-%d %H:%M:%S,")),
    logfile.write(reason),
    logfile.write("\n")
    logfile.close()


def log_alerts(notification):
    '''Log all email sms alerts'''
    alert_log = open("/home/pi/raspi-sump/logs/alert_log", 'a')
    alert_log.write(time.strftime("%Y-%m-%d %H:%M:%S,")),
    alert_log.write(notification),
    alert_log.write("\n")
    alert_log.close()


def log_errors(notification):
    '''Log all errors'''
    error_log = open("/home/pi/raspi-sump/logs/error_log", 'a')
    error_log.write(time.strftime("%Y-%m-%d %H:%M:%S,")),
    error_log.write(notification),
    error_log.write("\n")
    error_log.close()


def log_heartbeat(notification):
    '''Log all email sms heartbeat notification failures'''
    heartbeat_log = open("/home/pi/raspi-sump/logs/heartbeat_log", 'a')
    heartbeat_log.write(time.strftime("%Y-%m-%d %H:%M:%S,")),
    heartbeat_log.write(notification),
    heartbeat_log.write("\n")
    heartbeat_log.close()

