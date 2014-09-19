#!/usr/bin/python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/

"""
The MIT License (MIT)

Copyright (c) 2014 Raspi-Sump

Permission is hereby granted, free of charge, to any person obtaining a copy
of Raspi-Sump and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included
    in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
"""

# Note
"""Only use this file if you need to take a reading more often than once
per minute.  You should rename this file raspisump.py replacing the other
version. For any interval longer than 60 seconds consider using the main
raspisump.py file with cron instead.  This file uses a while loop to
continuously run.  It should be run in conjunction with checkpid.py to
monitor the health of the raspisump process.
"""

import time
import decimal
import smtplib
import string
import ConfigParser
import RPi.GPIO as GPIO

config = ConfigParser.RawConfigParser()
config.read('/home/pi/raspi-sump/.raspisump.conf')

# Do not modify these variables
# Use .raspisump.conf for all configurations


def water_level():
    """Measure the distance of water using the HC-SR04 Ultrasonic Sensor."""
    trig_pin = config.getint('gpio_pins', 'trig_pin')
    echo_pin = config.getint('gpio_pins', 'echo_pin')
    critical_distance = config.getint('pit', 'critical_distance')
    pit_depth = config.getint('pit', 'pit_depth')
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    try:
        while True:
            sample = []
            for error_margin in range(11):
                GPIO.setup(trig_pin, GPIO.OUT)
                GPIO.setup(echo_pin, GPIO.IN)

                GPIO.output(trig_pin, GPIO.LOW)
                time.sleep(0.3)
                GPIO.output(trig_pin, True)
                time.sleep(0.00001)
                GPIO.output(trig_pin, False)

                while GPIO.input(echo_pin) == 0:
                    sonar_signal_off = time.time()
                while GPIO.input(echo_pin) == 1:
                    sonar_signal_on = time.time()

                time_passed = sonar_signal_on - sonar_signal_off

                # Speed of sound is 34,322 cm/sec at 20d Celcius (divide by 2)
                distance_cm = time_passed * 17161
                sample.append(distance_cm)

                GPIO.cleanup()
            handle_error(sample, critical_distance, pit_depth)

    except KeyboardInterrupt:
        print "Script killed by user"


def handle_error(sample, critical_distance, pit_depth):
    """Eliminate fringe error readings by using the median reading of a
    sorted sample."""
    sorted_sample = sorted(sample)
    sensor_distance = sorted_sample[5]  # median reading
    water_depth = pit_depth - sensor_distance
    filename = "/home/pi/raspi-sump/csv/waterlevel-%s.csv" % time.strftime(
               "%Y%m%d"
    )
    capture = open(filename, 'a')

    if water_depth > critical_distance:
        smtp_alerts(water_depth, capture)
    else:
        level_good(water_depth, capture)


def level_good(how_far, target):
    """Process reading if level is less than critical distance."""
    reading_interval = config.getint('pit', 'reading_interval')
    decimal.getcontext().prec = 3
    how_far_clean = decimal.Decimal(how_far) * 1
    target.write(time.strftime("%H:%M:%S,")),
    target.write(str(how_far_clean)),
    target.write("\n")
    target.close()
    time.sleep(reading_interval)


def smtp_alerts(how_far, target):
    """Process reading and generate alert if level greater than critical
    distance."""
    reading_interval = config.getint('pit', 'reading_interval')
    smtp_authentication = config.getint('email', 'smtp_authentication')
    smtp_tls = config.getint('email', 'smtp_tls')
    smtp_server = config.get('email', 'smtp_server')
    email_to = config.get('email', 'email_to')
    email_from = config.get('email', 'email_from')

    decimal.getcontext().prec = 3
    how_far_clean = decimal.Decimal(how_far) * 1

    target.write(time.strftime("%H:%M:%S,")),
    target.write(str(how_far_clean)),
    target.write("\n")
    target.close()

    email_body = string.join((
        "From: %s" % email_from,
        "To: %s" % email_to,
        "Subject: Sump Pump Alert!",
        "",
        "Critical! The sump pit water level is %s cm." % str(
            how_far_clean
        ),), "\r\n"
        )

    server = smtplib.SMTP(smtp_server)

    if smtp_tls == 1:
        server.starttls()
    else:
        pass

    if smtp_authentication == 1:
        username = config.get('email', 'username')
        password = config.get('email', 'password')
        server.login(username, password)
    else:
        pass

    server.sendmail(email_from, email_to, email_body)
    server.quit()
    time.sleep(reading_interval)

if __name__ == "__main__":
    water_level()
