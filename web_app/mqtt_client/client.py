from paho.mqtt.client import Client as MQTTClient
from flask import current_app
from web_app import db
from web_app.models import Device
import time


class FlaskMQTT(MQTTClient):

    def __init__(self, app=None, *args, **kwargs):
        self.app = app
        self.min_time = 1
        self.max_time = 10
        self.connected = False
        super().__init__(*args[1:], **kwargs)
        self.reconnect_delay_set(min_delay=self.min_time, max_delay=self.max_time)
        self.topic_register = f'home/register'
        self.rc = 0
        self.exit = False

    def init_app(self, app):
        self.app = app

    def on_connect(self, mqttc, obj, flags, rc):
        print(f"flask_app connected to broker")

        # subscribe topics
        self.subscribe(topic=self.topic_register, qos=2)


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

        self.disconnect()

    def run(self, broker, port, keepalive):

        # set callback on message for bulb light topic
        self.message_callback_add(self.topic_register, self.register_device)
        #self.message_callback_add(self.topic_light_get, self.on_message_light_status)

        while not self.connected and not self.exit:
            self.try_connect(broker, port, keepalive)

        self.loop_start()

    def register_device(self, mosq, obj, msg):
        device_name = msg.payload.decode("utf-8")

        with self.app.app_context():
            # find device in db, if not exists add to db
            find_model = Device.query.filter_by(name=device_name).first()
            if find_model is None:
                device = Device(name=device_name, status=True)
                try:

                    db.session.add(device)
                    db.session.commit()
                except Exception as E:
                    print(E)
                    db.session.rollback()


