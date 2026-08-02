import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv

load_dotenv()

MQTT_LOGIN = os.getenv("MQTT_LOGIN")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_ADDRESS = os.getenv("MQTT_ADDRESS")
MQTT_PORT = os.getenv("MQTT_PORT")

mqtt_client: mqtt.Client | None = None

def init_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.username_pw_set(MQTT_LOGIN, MQTT_PASSWORD)
    mqtt_client.connect_async(MQTT_ADDRESS, int(MQTT_PORT))
    mqtt_client.loop_start()


def stop_mqtt():
    global mqtt_client
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()