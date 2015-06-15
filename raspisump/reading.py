''' Module to take a water_level reading.'''

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

import ConfigParser
import hcsr04sensor.sensor as sensor
import raspisump.log as log
import raspisump.alerts as alerts

config = ConfigParser.RawConfigParser()
config.read('/home/pi/raspi-sump/raspisump.conf')

configs = {'critical_water_level': config.getint('pit', 'critical_water_level'),
           'pit_depth': config.getint('pit', 'pit_depth'),
           'temperature': config.getint('pit', 'temperature'),
           'trig_pin': config.getint('gpio_pins', 'trig_pin'),
           'echo_pin': config.getint('gpio_pins', 'echo_pin'),
           'unit': config.get('pit', 'unit')
           }

# If item in raspisump.conf add to configs dict above
try:
    configs['alert_when'] = config.get('pit', 'alert_when')

# if not in raspisump.conf , provide a default value
except ConfigParser.NoOptionError:
    configs['alert_when'] = 'high'


def water_reading():
    '''Initiate a water level reading.'''
    pit_depth = configs['pit_depth']
    critical_water_level = configs['critical_water_level']
    trig_pin = configs['trig_pin']
    echo_pin = configs['echo_pin']
    round_to = 1
    temperature = configs['temperature']
    unit = configs['unit']

    value = sensor.Measurement(trig_pin, echo_pin, temperature, unit, round_to)
    raw_distance = value.raw_distance()

    if unit == 'imperial':
        water_depth = value.depth_imperial(raw_distance, pit_depth)
    if unit == 'metric':
        water_depth = value.depth_metric(raw_distance, pit_depth)

    generate_log(water_depth)
    generate_alert(water_depth, critical_water_level)


def generate_log(water_depth):
    '''Log water level reading to a file.'''
    log.log_reading(water_depth)


def generate_alert(water_depth, critical_water_level):
    '''Determine if an alert is required and initiate one if it is.'''
    if water_depth > critical_water_level and configs['alert_when'] == 'high':
        alerts.determine_if_alert(water_depth)
    elif water_depth < critical_water_level and configs['alert_when'] == 'low':
        alerts.determine_if_alert(water_depth)
    else:
        pass
