from lighting_devices.bulb import Bulb
from lighting_devices.bulb_iot import BulbMQTT
#from pynput.keyboard import Key, Listener
from functools import partial
from config import Config
from paho.mqtt.client import MQTTv311
from threading import Thread


# def on_press_disconnect(key,  mqtt_clients):
#     """
#     if ESC is pressed, send disconnect and exit
#     :param key:
#     :param mqtt_client:
#     :return:
#     """
#     if key == Key.esc:
#         for mqtt_client in mqtt_clients:
#             if mqtt_client.connected:
#                 mqtt_client.send_disconnect()
#
#             mqtt_client.exit = True


rooms = ['Bedroom', 'Kitchen', 'Living_room']
bulbs = []
mqtt_clients = []

# create clients for every room
for room in rooms:

    temp_bulb = Bulb(room, True, False)
    mqtt_clients.append(BulbMQTT(temp_bulb, client_id=temp_bulb.name, clean_session=True, protocol=MQTTv311))
    bulbs.append(temp_bulb)

# run clients in threads
for client in mqtt_clients:
    run_client = Thread(target=client.run, args=(Config.MQTT_BROKER_URL, Config.MQTT_BROKER_PORT, Config.MQTT_KEEPALIVE))
    run_client.start()


# set listener for key press, if ESC, send disconnect
# listener = Listener(
#             on_press=partial(on_press_disconnect, mqtt_clients=mqtt_clients))
# listener.start()