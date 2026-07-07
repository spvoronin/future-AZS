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

MQTT_topic = ""


def calib_data(data):
    clear_data = {
        "key" : data["uuid"],
        "uuid" : data["uuid"],
        "station_id": data["station_id"],
        "electric_current": data["electric_current"],
        "flame": True if data["flame"] >= 100 else False,
        "gas": data["gas"],
        "ambient_humidity": data["ambient_humidity"],
        "ambient_temperature": data["ambient_temperature"],
        "tank_temperature": int(data["tank_temperature"]),
        "water_level": round((data["water_level"] / 1023) * 100, 2)
    }
    return clear_data


def on_message(client, userdata, msg):
    print(f"Топик: {msg.topic}, Сообщение: {msg.payload.decode()}, Тип данных {type(msg.payload.decode())}")
    data = json.loads(msg.payload.decode())
    clear_data = calib_data(data)
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                "insert into sensors(uuid, station_id, electric_current, flame, gas, ambient_humidity, ambient_temperature, tank_temperature, water_level) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (clear_data["uuid"], clear_data["station_id"], clear_data["electric_current"], clear_data['flame'],
                 clear_data["gas"], clear_data["ambient_humidity"], clear_data["ambient_temperature"],
                 clear_data["tank_temperature"], clear_data["water_level"]))
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
