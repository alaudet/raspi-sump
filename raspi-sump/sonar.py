#!/usr/bin/python

# raspi-sump, a sump pump monitoring system
# Al Audet

import time
import RPi.GPIO as GPIO
import decimal

def reading():
    
    GPIO.setwarnings(False)
    
    GPIO.setmode(GPIO.BCM)
    
    run = 1
    try:
        while run == 1:
        
            GPIO.setup(17,GPIO.OUT)
            GPIO.setup(27,GPIO.IN)
            GPIO.output(17, GPIO.LOW)
            
            time.sleep(0.3)
            
            GPIO.output(17, True)
            
            time.sleep(0.00001)
            
            GPIO.output(17, False)

            while GPIO.input(27) == 0:
                signaloff = time.time()
                
            while GPIO.input(27) == 1:
                signalon = time.time()
                
            timepassed = signalon - signaloff
                      
            decimal.getcontext().prec = 3
            distance = decimal.Decimal(timepassed) * 17000
            
            distance_cm = distance
            
            if distance_cm >= 85:  # for testing only
                print "> Higher than 85"

            elif distance_cm < 84 : # for testing only
                print "< Lower than 84"
            
            
            print distance_cm
             
            GPIO.cleanup()
            time.sleep(10)
    
    except KeyboardInterrupt:
        print "Script killed by user"
    

reading()
