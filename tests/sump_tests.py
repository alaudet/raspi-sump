from nose.tools import *
import raspisump.reading as reading
import raspisump.alerts as alerts
try:
    import ConfigParser as configparser  # Python2
except ImportError:
    import configparser  # Python3

config = configparser.RawConfigParser()
config.read('/home/pi/raspi-sump/raspisump.conf')

configs = {'pit_depth': config.getint('pit', 'pit_depth'),
           'unit': config.get('pit', 'unit')
           }

try:
    configs['alert_when'] = config.get('pit', 'alert_when')
except configparser.NoOptionError:
    configs['alert_when'] = 'high'

def test_water_reading():

    pit_depth = configs['pit_depth']
    value = reading.water_reading()
    assert type(value) == float
    assert pit_depth > value


def test_unit_types():
    
    measurement = alerts.unit_types()
    assert type(measurement) == str
    try:
        assert_equals(measurement, 'inches')
    except:
        assert_equals(measurement, 'centimeters')


def test_email_content():
    
    water_depth = 35 
    email_contents = alerts.email_content(water_depth)
    assert type(email_contents) == str
    beg, sep, end = email_contents.partition('Subject: ')
    assert_equals(beg[0:5], 'From:')
    try:
        assert_equals(end[0:9], 'Low Water')
    except:
        assert_equals(end[0:9], 'Sump Pump')
