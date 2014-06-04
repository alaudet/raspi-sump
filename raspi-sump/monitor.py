#!/usr/bin/python

# raspi-sump, a sump pump monitoring system
# Al Audet

# from sys import argv
import time
import RPi.GPIO as GPIO
import decimal
import smtplib
import string

# will do this later. Printing to screen for now
# script, filename = argv

def waterlevel():

    trig_pin = 17  #gpio pin 17 connected to Trig on HC-SR04 sensor
    echo_pin = 27  #gpio pin 27 connected to Echo on HC-SR04 sensor 
    critical_distance = 88.6 # distance in cm, just for testing, will be much shorter

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    
    run = 1
    try:
        while run == 1:
        
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
                      
            decimal.getcontext().prec = 3 # readings to one decimal place
            distance_cm = decimal.Decimal(time_passed) * 17000
                    
            GPIO.cleanup()
            
            if distance_cm < critical_distance:
                smtp_alerts(distance_cm) 
             
            else:
                level_good(distance_cm)   
    
    except KeyboardInterrupt:
        print "Script killed by user"
        #target.close()

def level_good(how_far):
    
    # print to screen is good enough for now
    # later dump to file and upload offsite for processing
    print time.strftime("%H:%M:%S,"),
    print how_far
    #target.write(time.strftime("%H:%M:%S,")),
    #target.write(str(length)),
    #target.write("\n")
    time.sleep(5)
    

def smtp_alerts(how_far):
    
    #username = "username"
    #password = "secret"
    
    email_from = 'your_email@gmail.com'
    email_to = 'recipient@somewhere.com'
    email_body = string.join((
        "From: %s" % email_from,
        "To: %s" % email_to,
        "Subject: Sump Pump Alert!",
        "",
        "The sump pump level is at %f cm!" % how_far,
        ), "\r\n")
    
    #tested email alert working.  print to screen good enough for now
    print email_from
    print email_to
    print email_body

    # will also write the values to file later

    #server = smtplib.SMTP("smtp.gmail.com:587")
    #server.starttls()
    #server.login(username, password)
    #server.sendmail(email_from, email_to, email_body)
    #server.quit()
    time.sleep(15)

if __name__ == "__main__":
    #target = open(filename, 'a')
    waterlevel()
