''' Module for measuring distance or depth with an HCSRO4 Ultrasonic sound 
sensor and a Raspberry Pi.  Imperial and Metric measurements are available'''

# Al Audet
# MIT License

import time
import math
import RPi.GPIO as GPIO


class Measurement(object):
    '''Create a measurement using a HC-SR04 Ultrasonic Sensor connected to 
    the GPIO pins of a Raspberry Pi.'''
    def __init__(self, trig_pin, echo_pin, temperature, unit, round_to):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.temperature = temperature
        self.unit = unit
        self.round_to = round_to

    def raw_distance(self):
        '''Return an error corrected unrounded distance, in cm, of an object 
        adjusted for temperature in Celcius.  The distance calculated
        is the median value of a sample of 11 readings.'''
        if self.unit != 'metric' and self.unit != 'imperial':
            print "Unit Type Error: Unit must be imperial or metric"
            exit(0)
        if self.unit == 'imperial':
            self.temperature = (self.temperature - 32) * 0.5556
        speed_of_sound = 331.3 * math.sqrt(1+(self.temperature / 273.15))
        sample = []
        for distance_reading in range(11):
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.trig_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.output(self.trig_pin, GPIO.LOW)
            time.sleep(0.3)
            GPIO.output(self.trig_pin, True)
            time.sleep(0.00001)
            GPIO.output(self.trig_pin, False)
            while GPIO.input(self.echo_pin) == 0:
                sonar_signal_off = time.time()
            while GPIO.input(self.echo_pin) == 1:
                sonar_signal_on = time.time()
            time_passed = sonar_signal_on - sonar_signal_off
            distance_cm = time_passed * ((speed_of_sound * 100) / 2)
            sample.append(distance_cm)
            GPIO.cleanup()
        sorted_sample = sorted(sample)
        return sorted_sample[5]

    def depth_metric(self, median_reading, hole_depth):
        '''Calculate the rounded metric depth of a liquid. hole_depth is the
        distance, in cm's, from the sensor to the bottom of the hole.'''
        return round(hole_depth - median_reading, self.round_to)

    def depth_imperial(self, median_reading, hole_depth):
        '''Calculate the rounded imperial depth of a liquid. hole_depth is the
        distance, in inches, from the sensor to the bottom of the hole.'''
        return round(hole_depth - (median_reading * 0.394), self.round_to)

    def distance_metric(self, median_reading):
        '''Calculate the rounded metric distance, in cm's, from the sensor
        to an object'''
        return round(median_reading, self.round_to)

    def distance_imperial(self, median_reading):
        '''Calculate the rounded imperial distance, in inches, from the sensor
        to an oject.'''
        return round(median_reading * 0.394, self.round_to)
