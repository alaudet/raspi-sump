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
                distance_cm = time_passed * 17000
                
                sample.append(distance_cm)
                
                GPIO.cleanup()

            handle_error(sample, critical_distance)
    
    except KeyboardInterrupt:
        print "Script killed by user"
        #target.close()


def handle_error(sample, critical_distance):
    
    sorted_sample = sorted(sample)
    true_distance = sorted_sample[5] # median reading
    
    if true_distance < critical_distance:
        smtp_alerts(true_distance) 
             
    else:
        level_good(true_distance)   


def level_good(how_far):
    
    # print to screen is good enough for now
    # later dump to file and upload offsite for processing
    print time.strftime("%H:%M:%S,"),
    decimal.getcontext().prec = 3 
    how_far_clean = decimal.Decimal(how_far) * 1
    print how_far_clean
    #target.write(time.strftime("%H:%M:%S,")),
    #target.write(str(length)),
    #target.write("\n")
    #time.sleep(5)
    

def smtp_alerts(how_far):
    
      
    #username = "raspi-sump@example.com"
    #password = "secret"
    
    print time.strftime("%H:%M:%S,"),
    decimal.getcontext().prec = 3 
    how_far_clean = decimal.Decimal(how_far) * 1
    print how_far_clean
    
    email_from = 'raspi-sump@example.com'
    email_to = 'my_cell_number@wireless_carrier.com'
    email_body = string.join((
        "From: %s" % email_from,
        "To: %s" % email_to,
        "Subject: Sump Pump Alert!",
        "",
        "The sump pump level is at %s cm!" % str(how_far_clean),
        ), "\r\n")

    print "Send email"

    #target.write(time.strftime("%H:%M:%S,")),
    #target.write(str(length)),
    #target.write("\n")
    
   # server = smtplib.SMTP("smtp.gmail.com:587")
   # server.starttls()
   # server.login(username, password)
   # server.sendmail(email_from, email_to, email_body)
   # server.quit()
   # time.sleep(10)

if __name__ == "__main__":
    #target = open(filename, 'a')
    waterlevel()
