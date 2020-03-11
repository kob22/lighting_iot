from lighting_devices.bulb import Bulb
from lighting_devices.bulb_iot import BulbMQTT
from paho.mqtt.client import MQTTv311
from tests.cases.conftest import TestConfig as Config
import time
import mock
from paho.mqtt.client import Client as MQTTClient
import threading


class Callbacks():

    def __init__(self):
        self.messages = []

    def published(self, client, userdata, message):
        self.messages.append(message)
        return True


class TestMQTTDevice(object):

    def setup_method(self, method):

        self.light_room = Bulb('Room_Light', False, False)
        self.light_room_client = BulbMQTT(self.light_room, client_id=self.light_room.name, clean_session=True, protocol=MQTTv311)

    def test_connection(self, mqtt_broker_start):

        # check if not connected
        assert self.light_room_client.connected is False

        # check connection and mock rc to exit
        with mock.patch.object(self.light_room_client, 'rc', 1) as d:
            self.light_room_client.run(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
            assert self.light_room_client.connected is True
            self.light_room_client.disconnect()

    def test_reconnect(self, mqtt_broker_start):

        # check if not connected
        assert self.light_room_client.connected is False

        # try connect
        self.light_room_client.try_connect("127.0.1.2", 8900, 3)
        assert self.light_room_client.connected is False

        # try reconnect
        self.light_room_client.try_connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)
        assert self.light_room_client.connected is True

        self.light_room_client.disconnect()

    def test_on_disconnect(self, mqtt_broker_start):
        self.callbacks = Callbacks()

        # set test client and set callback for msg
        self.test_client = MQTTClient(client_id='Test_client_X25235', clean_session=True, protocol=MQTTv311)
        self.test_client.message_callback_add(self.light_room_client.topic_bulb_status, self.callbacks.published)

        # connect test client, loop start and subscribe
        self.test_client.connect(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE)# connect to broker
        self.test_client.loop_start()
        self.test_client.subscribe(topic=self.light_room_client.topic_bulb_status, qos=2)

        # start thread with bulb client
        thread1 = threading.Thread(target=self.light_room_client.run, args = (Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE))
        thread1.start()
        time.sleep(2)
        assert self.light_room_client.connected is True

        self.light_room_client.send_disconnect()
        time.sleep(3)

        self.test_client.loop_stop()
        self.test_client.disconnect()
        assert len(self.callbacks.messages) == 2
        assert 'off' == self.callbacks.messages[1].payload.decode("utf-8")


    def test_on_reconnect_msg(self):
        pass

    def test_light_switch(self):
        pass
