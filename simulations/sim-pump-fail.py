#!/usr/bin/python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/

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
import decimal
import smtplib
import string
filename = "/home/al/pump_failure-{}.csv".format(time.strftime("%Y%m%d"))


def water_distance():
    """Measure the distance of water using the HC-SR04 Ultrasonic Sensor."""
    critical_distance = 35
    start_level = 30.0
    water_rising = 0.5
    print "When water level reaches {} cm's generate an email alert".format(
        critical_distance
        )
    time.sleep(3)

    try:
        while True:
            start_level += water_rising
            sample = [start_level for i in range(11)]
            handle_error(sample, critical_distance, filename)
    except KeyboardInterrupt:
        print "Script killed by user"


def handle_error(sample, critical_distance, filename):
    """Eliminate fringe error readings by using the median reading of a
    sorted sample."""
    sorted_sample = sorted(sample)
    true_distance = sorted_sample[5]
    capture = open(filename, 'a')

    if true_distance > critical_distance:
        smtp_alerts(true_distance, capture)
    else:
        level_good(true_distance, capture)


def level_good(how_far, target):
    """Process reading if level is greater than critical distance."""
    decimal.getcontext().prec = 3
    how_far_clean = decimal.Decimal(how_far) * 1
    print how_far_clean,
    print "Water Level Rising"
    target.write(time.strftime("%H:%M:%S,")),
    target.write(str(how_far_clean)),
    target.write("\n")
    target.close()
    time.sleep(1)


def smtp_alerts(how_far, target):
    """Process reading and generate alert if less than critical distance."""
    # username = "your smtp username here "
    # password = "your smtp password here"
    smtp_server = "localhost:25"

    decimal.getcontext().prec = 3
    how_far_clean = decimal.Decimal(how_far) * 1

    target.write(time.strftime("%H:%M:%S,")),
    target.write(str(how_far_clean)),
    target.write("\n")
    target.close()

    email_from = "Raspi-Sump <email@yourdomain.com>"
    email_to = "email@yourdomain.com or wireless sms email for sms alerts"
    email_body = string.join((
        "From: {}".format(email_from),
        "To: {}".format(email_to),
        "Subject: Sump Pump Alert!",
        "",
        "Critical! The sump pit water level is {} cm.".format(str(
            how_far_clean)),), "\r\n"
        )
    print ""
    print "Pump Failure!!! Critical Level Breached. Email Sent"
    time.sleep(1)
    print ""
    print email_from
    print email_to
    print email_body
    server = smtplib.SMTP(smtp_server)
    # server.starttls()
    # server.login(username, password)
    server.sendmail(email_from, email_to, email_body)
    server.quit()
    exit(0)

if __name__ == "__main__":
    water_distance()
