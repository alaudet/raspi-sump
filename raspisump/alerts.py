'''Module to send SMTP alerts in case of sump pump failure'''

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

import os
import time
import smtplib
from datetime import datetime
import string
import ConfigParser
from collections import deque
import csv
import raspisump.log as log

config = ConfigParser.RawConfigParser()
config.read('/home/pi/raspi-sump/raspisump.conf')

configs = {'email_to': config.get('email', 'email_to'),
           'email_from': config.get('email', 'email_from'),
           'smtp_authentication': config.getint(
               'email', 'smtp_authentication'),
           'smtp_tls': config.getint('email', 'smtp_tls'),
           'smtp_server': config.get('email', 'smtp_server'),
           'username': config.get('email', 'username'),
           'password': config.get('email', 'password'),
           'unit': config.get('pit', 'unit')
           }

# If item in raspisump.conf add to configs dict above
try:
    configs['alert_interval'] = config.getint('email', 'alert_interval')

# if not in raspisump.conf , provide a default value
except ConfigParser.NoOptionError:
    configs['alert_interval'] = 5 

# same idea as above.
try:
    configs['alert_when'] = config.get('pit', 'alert_when')

except ConfigParser.NoOptionError:
    configs['alert_when'] = 'high' 

def smtp_alerts(water_depth):
    '''Generate email alert if water level greater than critical distance.'''
    recipients = configs['email_to'].split(', ')
    unit = configs['unit']

    if unit == 'imperial':
        unit_type = 'inches'
    elif unit == 'metric':
        unit_type = 'centimeters'
    else:
        print "Error"

    if configs['alert_when'] == 'high':
        email_body = string.join((
            "From: {}".format(configs['email_from']),
            "To: {}".format(configs['email_to']),
            "Subject: Sump Pump Alert!",
            "",
            "Critical! The sump pit water level is {} {}.".format(
                str(water_depth), unit_type
            ),
            "Next alert in {} minutes".format(
                configs['alert_interval']
            ),), "\r\n"
            )

    if configs['alert_when'] == 'low':
        email_body = string.join((
            "From: {}".format(configs['email_from']),
            "To: {}".format(configs['email_to']),
            "Subject: Low Water Level Alert!",
            "",
            "Warning! The water level is down to {} {}.".format(
                str(water_depth), unit_type
            ),
            "Next alert in {} minutes".format(
                configs['alert_interval']
            ),), "\r\n"
            )

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


def determine_if_alert(water_depth):
    '''Determine if an alert is required.  Only send if last alert has been
    sent more than the amount of time identified in the raspisump.conf file.
    Entry in conf file is alert_interval under the [email] section.'''

    alert_interval = configs['alert_interval']

    alert_log = '/home/pi/raspi-sump/logs/alert_log'

    if not os.path.isfile(alert_log):
        smtp_alerts(water_depth)
        log.log_alerts('Email SMS Alert Sent')

    else:
        with open(alert_log, 'rb') as f:
            last_row = deque(csv.reader(f), 1)[0]
            last_alert_sent = last_row[0]
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            last_alert_time = datetime.strptime(
                last_alert_sent, '%Y-%m-%d %H:%M:%S'
            )
            time_now = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
            delta = (time_now - last_alert_time)
            minutes_passed = delta.seconds / 60
            
        if minutes_passed >= alert_interval:
            smtp_alerts(water_depth)
            log.log_alerts('Email SMS Alert Sent')

        else:
            pass
