import paho.mqtt.client as mqtt
import psycopg2
from dotenv import load_dotenv
import os
import json

load_dotenv()

MQTT_LOGIN = os.getenv("MQTT_LOGIN")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_ADDRESS = os.getenv("MQTT_ADDRESS")
MQTT_PORT = os.getenv("MQTT_PORT")

HOST = os.getenv("HOST")
NAME_USER = os.getenv("NAME_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
CONNECT = os.getenv("CONNECT")

MQTT_topic = "BV/SAF/sensors"


def on_message(client, userdata, msg):
    print(f"Топик: {msg.topic}, Сообщение: {msg.payload.decode()}, Тип данных {type(msg.payload.decode())}")
    data = json.loads(msg.payload.decode())
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                "insert into sensors(uuid, electric_current, flame, gas, ambient_humidity, ambient_temperature, tank_temperature, water_level, voltage) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (data["uuid"], data["electric_current"], data['flame'],
                 data["gas"], data["ambient_humidity"], data["ambient_temperature"],
                 data["tank_temperature"], data["water_level"], data["voltage"]))
    except Exception as e:
        print(f'[info]: Ошибка {e}')
    finally:
        if connection:
            connection.close()
            print('[info]: коннект закрыт')


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message  # Обработчик сообщений
client.username_pw_set(MQTT_LOGIN, MQTT_PASSWORD)  # Логин и пароль
client.connect(MQTT_ADDRESS, int(MQTT_PORT))  # Подключение
client.subscribe(MQTT_topic)  # Подписка на топик

client.loop_forever()  # Запуск цикла
