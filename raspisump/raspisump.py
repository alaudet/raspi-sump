#!/usr/bin/python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/

import time
import decimal
import smtplib
import string
import RPi.GPIO as GPIO

def water_level():
    """Measure the distance of water using the HC-SR04 Ultrasonic Sensor."""
    trig_pin = 17  # GPIO pin 17 connected to Trig on HC-SR04 sensor.
    echo_pin = 27  # GPIO pin 27 connected to Echo on HC-SR04 sensor. 
    critical_distance = 40 # Water level should not exceed this depth (cm).
    pit_depth = 72 # Distance from the sensor to the bottom of sump pit.
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    try:
        while True:
            sample = []
            for error_margin in range(11):
                GPIO.setup(trig_pin,GPIO.OUT)
                GPIO.setup(echo_pin,GPIO.IN)
                
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
    sensor_distance = sorted_sample[5] # median reading
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
    decimal.getcontext().prec = 3 
    how_far_clean = decimal.Decimal(how_far) * 1
    target.write(time.strftime("%H:%M:%S,")),
    target.write(str(how_far_clean)),
    target.write("\n")
    target.close()
    time.sleep(60)

def smtp_alerts(how_far, target):
    """Process reading and generate alert if level greater than critical 
    distance."""
    username = "your smtp username here "
    password = "your smtp password here"
    smtp_server = "smtp.gmail.com:587"

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
        "Sump pit water level above 40cm critical level. Currently at %s cm." % str(
        how_far_clean),), "\r\n"
        )
    
    server = smtplib.SMTP(smtp_server)
    server.starttls() 
    server.login(username, password) 
    server.sendmail(email_from, email_to, email_body)
    server.quit()
    time.sleep(60)

if __name__ == "__main__":
    water_level()
