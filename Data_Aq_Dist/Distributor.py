import paho.mqtt.client as mqtt
import time
import json

MQTT_BROKER = "localhost"
MQTT_PORT = 12345
MQTT_TOPIC = "sensor/speeduino_data"
MQTT_USERNAME = None # Add Credentials, if needed
MQTT_PASSWORD = None

class Distributor:
    def __init__(self):
        self.server = mqtt.Client()
        self.server.on_connect = self.on_connect
        if MQTT_USERNAME and MQTT_PASSWORD:
            self.server.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        try:
            self.server.connect(MQTT_BROKER, MQTT_PORT)
        except Exception as e:
            print(f"Connection failed, Error : {e}")
            time.sleep(5)
            return
        self.server.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
        else:
            print("Failed to connect, return code %d\n", rc)

    def distribute_data(self, data):
        try:
            if data:
                payload = json.dumps(data)
                self.server.publish(MQTT_TOPIC, payload, qos=0, retain=False)

        except KeyboardInterrupt:
            print("Keyboard interrupt")
        except Exception as e:
            print(f"Error : {e}")
        finally:
            self.server.loop_stop()
            self.server.disconnect()
            print("Distributor Stopped and cleaned up")


