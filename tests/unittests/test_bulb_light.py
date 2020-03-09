from lighting_devices.bulb import LightBulb
from pytest import raises


def test_set_not_boolean_light():

    with raises(TypeError) as excinfo:
        light = LightBulb('Bedroom_Light', 1, 0)
    assert "Light must be a boolean" in str(excinfo.value)


def test_set_not_boolean_status():

    with raises(TypeError) as excinfo:
        light = LightBulb('Bedroom_Light', False, 0)
    assert "Status must be a boolean" in str(excinfo.value)


def test_set_get():

    bedroom_light = LightBulb('Bedroom_Light', True, True)
    assert bedroom_light.light is True
    assert bedroom_light.status is True

    bedroom_light.light = False
    bedroom_light.status = False
    assert bedroom_light.light is False
    assert bedroom_light.status is False
