import ConfigParser
import raspisump.sensor as sensor
import raspisump.log as log
import raspisump.alerts as alerts

config = ConfigParser.RawConfigParser()
config.read('/home/pi/raspi-sump/raspisump.conf')

configs = {'critical_distance': config.getint('pit', 'critical_distance'),
           'pit_depth': config.getint('pit', 'pit_depth'),
           'temperature': config.getint('pit', 'temperature'),
           'trig_pin': config.getint('gpio_pins', 'trig_pin'),
           'echo_pin': config.getint('gpio_pins', 'echo_pin')
           }

def water_reading():
    pit_depth = configs['pit_depth']
    critical_distance = configs['critical_distance']
    trig_pin = configs['trig_pin']
    echo_pin = configs['echo_pin']
    rounded_to = 1 
    temperature = configs['temperature']

    value = sensor.Measurement(trig_pin, echo_pin, rounded_to, temperature)
    water_depth = pit_depth - value.distance()
    generate_log(water_depth)
    generate_alert(water_depth, critical_distance)

def generate_log(water_depth):
    log.log_reading(water_depth)

def generate_alert(water_depth, critical_distance):
    if water_depth > critical_distance:
        alerts.smtp_alerts(water_depth)
    else:
        pass
