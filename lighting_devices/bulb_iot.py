from paho.mqtt.client import Client as MQTTClient
import time
import json

class BulbMQTT(MQTTClient):

    def __init__(self, *args, **kwargs):
        self.bulb = args[0]
        self.min_time = 1
        self.max_time = 10
        self.connected = False
        super().__init__(*args[1:], **kwargs)
        self.reconnect_delay_set(min_delay=self.min_time, max_delay=self.max_time)
        self.topic_bulb_status = f'home/light/{self.bulb.name}/status'
        self.topic_bulb_get = f'home/light/{self.bulb.name}/get'
        self.topic_light_set = f'home/light/{self.bulb.name}/light/set'
        self.topic_light_status = f'home/light/{self.bulb.name}/light/status'
        self.topic_light_get = f'home/light/{self.bulb.name}/light/get'
        self.topic_register = f'home/register'
        self.rc = 0
        self.exit = False

    def on_connect(self, mqttc, obj, flags, rc):
        print(f"{self.bulb.name} connected to broker")

        # set bulb status
        self.bulb.status = True

        # subscribe topics
        self.subscribe(topic=self.topic_bulb_get, qos=2)
        self.subscribe(topic=self.topic_light_set, qos=2)
        self.subscribe(topic=self.topic_light_get, qos=2)

        # set will_set device status to off after disconnects without disconnect()
        self.will_set(topic=self.topic_bulb_status, payload="off", qos=2, retain=True)

        # register device
        msg_register = {'name': self.bulb.name, 'light': self.bulb.light, 'status': self.bulb.status}
        self.publish(topic=self.topic_register, payload=json.dumps(msg_register), qos=2)

        # publish bulb light and status
        self.publish(topic=self.topic_bulb_status, payload=self.bulb_status_payload(), qos=2)
        self.publish(topic=self.topic_light_status, payload=self.bulb_light_status_payload(), qos=2)

    def on_disconnect(self, mqttc, obj, msg):
        print('send disconnect')
        time.sleep(2)

    def on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

    def on_publish(self, mqttc, obj, mid):
        print("mid: "+str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def try_connect(self, broker, port, keepalive):
        try:
            self.connect(broker, port, keepalive)
            self.connected = True
        # catch all, ConnectionRefusedError, socket.timeout don't inherit from BaseException
        except Exception as e:
            print(f'Connection refused, I will try in {self.min_time} seconds, error {e}')
            self.connected = False
            time.sleep(self.min_time)

    def send_disconnect(self):
        self.bulb.status = False
        wait = self.publish(topic=self.topic_bulb_status, payload=self.bulb_status_payload(), qos=2)

        wait.wait_for_publish()
        self.disconnect()

    def run(self, broker, port, keepalive):

        # set callback on message for bulb light topic
        self.message_callback_add(self.topic_light_set, self.on_message_light_switch)
        self.message_callback_add(self.topic_light_get, self.on_message_light_status)

        while not self.connected and not self.exit:
            self.try_connect(broker, port, keepalive)

        while self.rc == 0:
            self.rc = self.loop()

        return self.rc

    def bulb_light_status_payload(self):
        """
        Generates message to publish from bulb light
        :return: on/off message for publish
        """
        if self.bulb.light:
            return "on"
        else:
            return "off"

    def bulb_status_payload(self):
        """
        Generates message to publish from bulb status
        :return: on/off message for publish
        """
        if self.bulb.status:
            return "on"
        else:
            return "off"

    def on_message_light_switch(self, mosq, obj, msg):
        """
        Set bulb light from message
        """
        message = msg.payload.decode("utf-8")
        if message == 'on':
            self.bulb.light = True
        elif message == 'off':
            self.bulb.light = False
        print(self.bulb.light)
        self.publish(topic=self.topic_light_status, payload=self.bulb_light_status_payload(), qos=2)

    def on_message_light_status(self, mosq, obj, msg):
        """
        On topic light bulb light from message
        """
        self.publish(topic=self.topic_light_status, payload=self.bulb_light_status_payload(), qos=2)

# todo space in name?
# sending light status or asking for light status



