import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

load_dotenv()

MQTT_LOGIN = os.getenv("MQTT_LOGIN")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_ADDRESS = os.getenv("MQTT_ADDRESS")
MQTT_PORT = os.getenv("MQTT_PORT")

def init_mqtt() -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(MQTT_LOGIN, MQTT_PASSWORD)
    client.connect_async(MQTT_ADDRESS, int(MQTT_PORT))
    client.loop_start()
    return client


def stop_mqtt(client: mqtt.Client | None):
    if client:
        client.loop_stop()
        client.disconnect()