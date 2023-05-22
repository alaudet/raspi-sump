'''Send Heartbeat alert to test that email notifications are working.'''

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
import configparser
from collections import deque
import csv
from raspisump import log, alerts


config = configparser.RawConfigParser()
user = os.getlogin()
config.read('/home/' + user + '/raspi-sump/raspisump.conf')

configs = {'email_to': config.get('email', 'email_to'),
           'email_from': config.get('email', 'email_from'),
           'smtp_authentication': config.getint(
           'email', 'smtp_authentication'),
           'smtp_tls': config.getint('email', 'smtp_tls'),
           'smtp_server': config.get('email', 'smtp_server'),
           'username': config.get('email', 'username'),
           'password': config.get('email', 'password')
           }

try:
    configs['heartbeat_interval'] = config.getint('email',
                                                  'heartbeat_interval')
except configparser.NoOptionError:
    configs['heartbeat_interval'] = 10080


def get_last_alert_time():
    '''Retrieve the last alert time string from logfile'''
    heartbeat_log = '/home/' + user + '/raspi-sump/logs/heartbeat_log'
    with open(heartbeat_log, 'rt') as f:
        last_row = deque(csv.reader(f), 1)[0]
        return last_row[0]


def heartbeat_email_content():
    '''Build the contents of email body which will be sent as an alert'''
    heartbeat_interval_time = configs['heartbeat_interval']
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    last_alert = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
    future_date = last_alert + timedelta(minutes=heartbeat_interval_time + 1)

    weekday = future_date.strftime('%A')[0:3]
    month = future_date.strftime('%B')
    hour = future_date.strftime('%I')
    minute = future_date.strftime('%M')
    am_pm = future_date.strftime('%p').lower()

    time_of_day = alerts.current_time()
    hostname = alerts.host_name()
    subject = 'Subject: Raspi-Sump Heartbeat Notification'
    message = 'Raspi-Sump Email Notifications Working'

    return "\r\n".join((
        "From: {}".format(configs['email_from']),
        "To: {}".format(configs['email_to']),
        "{}".format(subject),
        "",
        "{} - {} - {}.".format(hostname, time_of_day, message),
        "Next heartbeat: {} {} {} at {}:{} {}".format(weekday,
                                                      month,
                                                      future_date.day,
                                                      hour,
                                                      minute,
                                                      am_pm),
        )
        )


def heartbeat_alerts():
    '''Send heartbeat email alert if water level greater
    than critical distance.'''
    recipients = configs['email_to'].split(', ')
    email_body = heartbeat_email_content()
    server = smtplib.SMTP(configs['smtp_server'])

    # Check if smtp server uses TLS
    if configs['smtp_tls'] == 1:
        server.starttls()
    else:
        pass
    # Check if smtp server uses authentication
    if configs['smtp_authentication'] == 1:
        username = configs['username']
        password = configs['password']
        server.login(username, password)
    else:
        pass

    server.sendmail(configs['email_from'], recipients, email_body)
    server.quit()


def determine_if_heartbeat():
    '''Determine if a heartbeat notification is required and if so, send
    the notification.'''

    heartbeat_log = '/home/' + user + '/raspi-sump/logs/heartbeat_log'
    if not os.path.isfile(heartbeat_log):
        heartbeat_alerts()
        log.log_event("heartbeat_log", "Heartbeat Email Sent")

    else:
        heartbeat_interval_time = configs['heartbeat_interval']
        last_email_sent = get_last_alert_time()
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        last_heartbeat_time = datetime.strptime(last_email_sent,
                                                '%Y-%m-%d %H:%M:%S')
        time_now = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
        delta = (time_now - last_heartbeat_time)
        minutes_passed = int((delta).total_seconds() / 60)

        if minutes_passed >= heartbeat_interval_time:
            heartbeat_alerts()
            log.log_event("heartbeat_log", "Heartbeat Email Sent")
        else:
            pass
