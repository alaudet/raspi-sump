#!/usr/bin/python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# No variables in this file need to be changed.  All configuration
# changes should be done in .raspisump.conf


"""
The MIT License (MIT)

Copyright (c) 2014 Al Audet

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
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
"""

import time
import smtplib
import string
import ConfigParser
import RPi.GPIO as GPIO


def water_distance():
    """Measure the distance of water using the HC-SR04 Ultrasonic Sensor."""
    trig_pin = config.getint('gpio_pins', 'trig_pin')
    echo_pin = config.getint('gpio_pins', 'echo_pin')
    critical_distance = config.getint('pit', 'critical_distance')
    pit_depth = config.getint('pit', 'pit_depth')
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
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


def handle_error(sample, critical_distance, pit_depth):
    """Eliminate fringe error readings by using the median reading of a
    sorted sample and log reading to file."""
    sorted_sample = sorted(sample)
    sensor_distance = sorted_sample[5]
    water_depth = round((pit_depth - sensor_distance), 1)
    log_reading(water_depth)
    if water_depth > critical_distance:
        smtp_alerts(water_depth)
    else:
        exit(0)


def smtp_alerts(water_depth):
    """Generate email alert if water level greater than critical distance."""
    email_to = config.get('email', 'email_to')
    email_from = config.get('email', 'email_from')
    email_body = string.join((
        "From: {}".format(email_from),
        "To: {}".format(email_to),
        "Subject: Sump Pump Alert!",
        "",
        "Critical! The sump pit water level is {} cm.".format(
            str(water_depth)
        ),), "\r\n"
        )

    smtp_authentication = config.getint('email', 'smtp_authentication')
    smtp_tls = config.getint('email', 'smtp_tls')
    smtp_server = config.get('email', 'smtp_server')
    server = smtplib.SMTP(smtp_server)
    # Check if smtp server uses TLS
    if smtp_tls == 1:
        server.starttls()
    else:
        pass
    # Check if smtp server uses authentication
    if smtp_authentication == 1:
        username = config.get('email', 'username')
        password = config.get('email', 'password')
        server.login(username, password)
    else:
        pass

    server.sendmail(email_from, email_to, email_body)
    server.quit()
    exit(0)


def log_reading(water_depth):
    """Log time and water depth reading."""
    time_of_reading = time.strftime("%H:%M:%S,")
    filename = "/home/pi/raspi-sump/csv/waterlevel-{}.csv".format(
        time.strftime("%Y%m%d")
    )
    csv_file = open(filename, 'a')
    csv_file.write(time_of_reading),
    csv_file.write(str(water_depth)),
    csv_file.write("\n")
    csv_file.close()

if __name__ == "__main__":
    config = ConfigParser.RawConfigParser()
    config.read('/home/pi/raspi-sump/raspisump.conf')
    water_distance()
