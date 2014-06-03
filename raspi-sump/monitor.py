#!/usr/bin/python

# raspi-sump, a sump pump monitoring system
# Al Audet

from sys import argv
import time
import RPi.GPIO as GPIO
import decimal

script, filename = argv

def waterlevel():

    trig_pin = 17  #gpio pin 17 connected to Trig on HC-SR04 sensor
    echo_pin = 27  #gpio pin 27 connected to Echo on HC-SR04 sensor 

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
                signaloff = time.time()
                
            while GPIO.input(echo_pin) == 1:
                signalon = time.time()
                
            timepassed = signalon - signaloff
                      
            decimal.getcontext().prec = 3 # readings to one decimal place
            distance = decimal.Decimal(timepassed) * 17000
            
            distance_cm = distance
            
            if distance_cm < 30:
                #add smtp code to alert if water reaches a certain level.
                pass

            target.write(time.strftime("%H:%M:%S,")),
            target.write(str(distance_cm)),
            target.write("\n")         
             
            GPIO.cleanup()
            time.sleep(10)
    
    except KeyboardInterrupt:
        print "Script killed by user"
        target.close()

target = open(filename, 'a')
waterlevel()
