from asyncio import open_unix_connection

import paho.mqtt.client as mqtt
import json

MQTT_USERNAME = None
MQTT_PASSWORD = None
MQTT_TOPIC = "sensor/speeduino_data"\
MQTT_Broker = "localhost"
MQTT_PORT = 12345

class MQTT_Client():
    def __init__(self):
        self.client = mqtt.Client()
        self.on_connect = self.on_connect
        self.on_message = self.on_message
        if MQTT_USERNAME and MQTT_PASSWORD:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        try:
            self.client.connect(MQTT_TOPIC, MQTT_PORT)
            self.client.loop_forever()

        except Exception as e:
            print(f"Connection failed, Error : {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
            self.client.subscribe(MQTT_TOPIC, qos=0)
            print("Subscribed to " + MQTT_TOPIC)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        try:
            msg = json.loads(msg.payload.decode())
            return msg

        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from message payload: {msg.payload.decode()}")
        except Exception as e:
            print(f"Error processing message: {e}")
