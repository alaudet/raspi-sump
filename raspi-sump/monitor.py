#!/usr/bin/python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/

from sys import argv
import time
import decimal
import smtplib
import string
import RPi.GPIO as GPIO

script, filename = argv

def water_level():

    trig_pin = 17  # GPIO pin 17 connected to Trig on HC-SR04 sensor.
    echo_pin = 27  # GPIO pin 27 connected to Echo on HC-SR04 sensor. 
    critical_distance = 30 

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    run = 1
    try:
        while run == 1:
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
            handle_error(sample, critical_distance)
    
    except KeyboardInterrupt:
        print "Script killed by user"
        target.close()

def handle_error(sample, critical_distance):
    sorted_sample = sorted(sample)
    true_distance = sorted_sample[5] # median reading
    
    if true_distance < critical_distance:
        smtp_alerts(true_distance) 
    else:
        level_good(true_distance)   

def level_good(how_far):
    decimal.getcontext().prec = 3 
    how_far_clean = decimal.Decimal(how_far) * 1
    
    print how_far_clean # only while testing
    
    target.write(time.strftime("%H:%M:%S,")),
    target.write(str(how_far_clean)),
    target.write("\n")
    time.sleep(5)
    
def smtp_alerts(how_far): 
    username = "your smtp username here "
    password = "your smtp password here"
    smtp_server = "smtp.gmail.com:587"

    decimal.getcontext().prec = 3 
    how_far_clean = decimal.Decimal(how_far) * 1
    
    print how_far_clean, # only while testing
    print "email sent" # only while testing
    
    target.write(time.strftime("%H:%M:%S,")),
    target.write(str(how_far_clean)),
    target.write("\n")
       
    email_from = "sender email"
    email_to = "recipient email or wireless carrier sms #"
    email_body = string.join((
        "From: %s" % email_from,
        "To: %s" % email_to,
        "Subject: Sump Pump Alert!",
        "",
        "Critical! The sump pit water level is at %s cm from the lid." % str(
        how_far_clean),), "\r\n"
        )
    
    print email_from # only while testing
    print email_to # only while testing
    print email_body #only while testing
   
    server = smtplib.SMTP(smtp_server)
    server.starttls() 
    server.login(username, password) 
    server.sendmail(email_from, email_to, email_body)
    server.quit()
    time.sleep(5)

if __name__ == "__main__":
    target = open(filename, 'a')
    water_level()
