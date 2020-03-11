
from paho.mqtt.client import MQTTv311
from tests.cases.conftest import TestConfig as Config

from paho.mqtt.client import Client as MQTTClient
import time
from web_app.models import Device
import json

class TestAPI(object):

    def test_register_device(self, client, session, mqtt_broker_start):

        self.test_client = MQTTClient(client_id='Test_client_X25235', clean_session=True, protocol=MQTTv311)

        # connect test client
        self.test_client.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
        self.test_client.loop_start()
        self.test_client.subscribe(topic='home/register', qos=2)

        devices = Device.query.all()

        # register devices
        rooms = ['Bedroom', 'Kitchen', 'Living_room']

        for room in rooms:
            msg_register = {'name': room, 'light': 'on', 'status': 'off'}
            wait = self.test_client.publish(topic='home/register', payload=json.dumps(msg_register), qos=2)
            wait.wait_for_publish()
        time.sleep(2)
        devices = Device.query.all()
        assert len(devices) == 3
