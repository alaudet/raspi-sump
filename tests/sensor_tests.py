from nose.tools import *
import math
from raspisump.sensor import Measurement


def test_measurement():
    value = Measurement(17, 27, 20, 'metric', 1)

    assert_equal(value.trig_pin, 17)
    assert_equal(value.echo_pin, 27)
    assert_equal(value.temperature, 20)
    assert_equal(value.unit, 'metric')
    assert_equal(value.round_to, 1)


def test_imperial_temperature_and_speed_of_sound():
    value = Measurement(17, 27, 68, 'imperial', 1)
    raw_measurement = value.raw_distance()
    speed_of_sound = 331.3 * math.sqrt(1+(value.temperature / 273.15))

    assert_equal(value.temperature, 20.0016)
    assert type(raw_measurement) == float
    assert_equal(speed_of_sound, 343.21555930656075)


def test_imperial_measurements():
    value = Measurement(17, 27, 68, 'imperial', 1)
    raw_measurement = 26.454564846
    hole_depth = 25

    imperial_distance = value.distance_imperial(raw_measurement)
    imperial_depth = value.depth_imperial(raw_measurement, hole_depth)

    assert type(imperial_distance) == float
    assert_equal(imperial_distance, 10.4)
    assert_equal(imperial_depth, 14.6)


def test_metric_measurements():
    value = Measurement(17, 27, 20, 'metric', 1)
    raw_measurement = 48.80804985408
    hole_depth = 72

    metric_distance = value.distance_metric(raw_measurement)
    metric_depth = value.depth_metric(raw_measurement, hole_depth)

    assert_equal(metric_distance, 48.8)
    assert_equal(metric_depth, 23.2)
