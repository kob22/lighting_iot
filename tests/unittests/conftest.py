import pytest
from os.path import dirname
import os
import subprocess
from tests.paho_mqtt_testing.interoperability import mqtt
import signal
import time


class ConfigTest:
    BROKER_ADDRESS = "127.0.0.1"
    PORT = 1883
    KEEPALIVE = 60


@pytest.fixture(scope='session')
def mqtt_broker_start():

    cmd = f"python ./tests/paho_mqtt_testing/interoperability/startbroker.py"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)
    time.sleep(2)
    yield

    os.killpg(os.getpgid(p.pid), signal.SIGTERM)