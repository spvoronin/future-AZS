import os
import time
from analiz_num import photo_processing
from dotenv import load_dotenv
import io
import psycopg2
import paho.mqtt.client as mqtt

load_dotenv()

URL = os.getenv("URL")
UUID_CAM = os.getenv("UUID_CAM")

HOST = os.getenv("HOST")
NAME_USER = os.getenv("NAME_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
CONNECT = os.getenv("CONNECT")

MQTT_LOGIN = os.getenv("MQTT_LOGIN")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_ADDRESS = os.getenv("MQTT_ADDRESS")
MQTT_PORT = os.getenv("MQTT_PORT")

MQTT_topic_sub = "BV/SAF/cam/request"
MQTT_topic_pub = "BV/SAF/cam/response"

photo_handler = photo_processing(HOST, NAME_USER, PASSWORD, DATABASE, CONNECT, URL, UUID_CAM)


def on_message(client, userdata, msg):
    if msg.payload.decode() == 'photo':
        photo_handler.save_photo()
        resp = photo_handler.analiz_num()
        client.publish(MQTT_topic_pub, resp)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message  # Обработчик сообщений
client.username_pw_set(MQTT_LOGIN, MQTT_PASSWORD)  # Логин и пароль
client.connect(MQTT_ADDRESS, int(MQTT_PORT))  # Подключение
client.subscribe(MQTT_topic_sub)  # Подписка на топик

client.loop_forever()  # Запуск цикла