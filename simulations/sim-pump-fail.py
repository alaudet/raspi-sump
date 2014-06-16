#!/usr/bin/python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/

import time
import decimal
import smtplib
import string
filename = "/home/pi/raspi-sump/simulation/pump_failure-%s.csv" % time.strftime(
            "%Y%m%d"
            )

def water_level():
    """Measure the distance of water using the HC-SR04 Ultrasonic Sensor."""
    
    critical_distance = 30
    start_level = 31.0
    water_rising = 0.1
   
    try:
        while True:
            start_level -= water_rising
            sample = [start_level for i in range(11)]                 
            handle_error(sample, critical_distance, filename)
    
    except KeyboardInterrupt:
        print "Script killed by user"
        
def handle_error(sample, critical_distance, filename):

    """Eliminate fringe error readings by using the median reading of a
    sorted sample."""
    sorted_sample = sorted(sample)
    true_distance = sorted_sample[5] # median reading
    
    capture = open(filename, 'a')
    
    if true_distance < critical_distance:
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
    time.sleep(2)

def smtp_alerts(how_far, target):
    """Process reading and generate alert if less than critical distance."""
    #username = "your smtp username here "
    #password = "your smtp password here"
    #smtp_server = "smtp.gmail.com:587"
    
    decimal.getcontext().prec = 3 
    how_far_clean = decimal.Decimal(how_far) * 1
    
    target.write(time.strftime("%H:%M:%S,")),
    target.write(str(how_far_clean)),
    target.write("\n")
    target.close()   

    email_from = "Raspi-Sump <email@yourdomain.com>"
    email_to = "email@yourdomain.com or wireless sms email for sms alerts"
    email_body = string.join((
        "From: %s" % email_from,
        "To: %s" % email_to,
        "Subject: Sump Pump Alert!",
        "",
        "Critical! The sump pit water level is at %s cm from the lid." % str(
        how_far_clean),), "\r\n"
        )
    print ""
    print "Pump Failure!!! Critical Level Breached. Email Sent"
    time.sleep(1)
    print ""
    print email_from
    print email_to
    print email_body
    #server = smtplib.SMTP(smtp_server)
    #server.starttls() 
    #server.login(username, password) 
    #server.sendmail(email_from, email_to, email_body)
    #server.quit()
    exit(0)

if __name__ == "__main__":
    water_level()
