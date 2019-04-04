'''Send Heartbeat alert to test that email notifications are working.'''

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import os
import time
import smtplib
from datetime import datetime
try:
    import ConfigParser as configparser  # Python2
except ImportError:
    import configparser  # Python3
from collections import deque
import csv
from raspisump import log, alerts


config = configparser.RawConfigParser()

config.read('/home/pi/raspi-sump/raspisump.conf')

configs = {'email_to': config.get('email', 'email_to'),
           'email_from': config.get('email', 'email_from'),
           'smtp_authentication': config.getint(
           'email', 'smtp_authentication'),
           'smtp_tls': config.getint('email', 'smtp_tls'),
           'smtp_server': config.get('email', 'smtp_server'),
           'username': config.get('email', 'username'),
           'password': config.get('email', 'password'),
           'heartbeat_interval': config.getint('email', 'heartbeat_interval')
           }


def heartbeat_email_content():

    '''Build the contents of email body which will be sent as an alert'''

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
        "Next alert in {} minutes".format(configs['heartbeat_interval']),
        )
        )


def heartbeat_alerts():
    '''Send heartbeat email alert if water level greater than critical distance.'''
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

    '''Will add code here to write to the error log if email fails'''
    server.sendmail(configs['email_from'], recipients, email_body)
    server.quit()


def determine_if_heartbeat():
    '''Determine if a heartbeat notification is required and if so, send
    the notification.'''

    heartbeat_interval_time = configs['heartbeat_interval']
    heartbeat_log = '/home/pi/raspi-sump/logs/heartbeat_log'
    print(heartbeat_interval_time)
    if not os.path.isfile(heartbeat_log):
        #heartbeat_alerts()
        print("create file and send the email")
        log.log_heartbeat("Heartbeat Email Sent")

    else:
        with open(heartbeat_log, 'rt') as f:
            last_row = deque(csv.reader(f), 1)[0]
            print('last row is {}'.format(last_row))
            last_email_sent = last_row[0]
            print('last_row[0] is {} '.format(last_email_sent))
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            last_heartbeat_time = datetime.strptime(
                last_email_sent, '%Y-%m-%d %H:%M:%S'
            )
            time_now = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
            delta = (time_now - last_heartbeat_time)
            print(delta)
            print(time_now)
            print(last_heartbeat_time)
            print(current_time)
            print('delta is {} .'.format(delta))
            minutes_passed = int((delta).total_seconds() / 60)
            print(minutes_passed)

            if minutes_passed >= heartbeat_interval_time:
                #heartbeat_alerts()
                print("File created, send the email")
                log.log_heartbeat("Heartbeat Email Sent")
            else:
                #pass
                print("interval hasn't passed, don't send")
