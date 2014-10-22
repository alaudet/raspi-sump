'''Module to send SMTP alerts in case of sump pump failure'''

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

import smtplib
import string
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('/home/pi/raspi-sump/raspisump.conf')

configs = {'email_to': config.get('email', 'email_to'),
           'email_from': config.get('email', 'email_from'),
           'smtp_authentication': config.getint(
               'email', 'smtp_authentication'),
           'smtp_tls': config.getint('email', 'smtp_tls'),
           'smtp_server': config.get('email', 'smtp_server'),
           'username': config.get('email', 'username'),
           'password': config.get('email', 'password')
           }


def smtp_alerts(water_depth):
    """Generate email alert if water level greater than critical distance."""
    email_body = string.join((
        "From: {}".format(configs['email_from']),
        "To: {}".format(configs['email_to']),
        "Subject: Sump Pump Alert!",
        "",
        "Critical! The sump pit water level is {} cm.".format(
            str(water_depth)
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

    server.sendmail(configs['email_from'], configs['email_to'], email_body)
    server.quit()
