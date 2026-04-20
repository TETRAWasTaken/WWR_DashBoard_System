import queue

import paho.mqtt.client as mqtt
import json

MQTT_USERNAME = None
MQTT_PASSWORD = None
MQTT_TOPIC = "sensor/speeduino_data"
MQTT_Broker = "localhost"
MQTT_PORT = 1883

class MQTT_Client():
    def __init__(self, name):
        self.message_queue = queue.Queue()
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2, client_id=name)

    def start(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        if MQTT_USERNAME and MQTT_PASSWORD:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        try:
            self.client.connect(MQTT_Broker, MQTT_PORT)
        except Exception as e:
            print(f"Connection failed, Error : {e}")
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker")
            self.client.subscribe(MQTT_TOPIC, qos=1)
            print("Subscribed to " + MQTT_TOPIC)
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        try:
            msg = json.loads(msg.payload.decode())
            self.message_queue.put(msg)

        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from message payload: {msg.payload.decode()}")
        except Exception as e:
            print(f"Error processing message: {e}")

    def get_message(self):
        try:
            return self.message_queue.get(block=False)
        except queue.Empty:
            return None
