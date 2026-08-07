import aiomqtt
import psycopg2
from dotenv import load_dotenv
import os
import json
import asyncpg
import asyncio

load_dotenv()

MQTT_LOGIN = os.getenv("MQTT_LOGIN")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_ADDRESS = os.getenv("MQTT_ADDRESS")
MQTT_PORT = int(os.getenv("MQTT_PORT"))

HOST = os.getenv("HOST")
NAME_USER = os.getenv("NAME_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
CONNECT = os.getenv("CONNECT")

MQTT_topic = "BV/SAF/sensors"

async def handle_message(message: aiomqtt.Message, pool: asyncpg.Pool):
    try:
        payload_str = message.payload.decode()
        print(f"Топик: {message.topic}, Сообщение: {payload_str}")

        data = json.loads(payload_str)
        async with pool.acquire() as connection:
            query = """
                        INSERT INTO sensors (
                            uuid, electric_current, flame, gas, ambient_humidity, 
                            ambient_temperature, tank_temperature, water_level, voltage
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """
            await connection.execute(
                query,
                data["uuid"],
                data["electric_current"],
                data["flame"],
                data["gas"],
                data["ambient_humidity"],
                data["ambient_temperature"],
                data["tank_temperature"],
                data["water_level"],
                data["voltage"]
            )
            print("[info]: Данные успешно записаны в БД через asyncpg")

    except json.JSONDecodeError:
        print("[info]: Ошибка декодирования JSON")
    except Exception as e:
        print(f"[info]: Ошибка обработки сообщения: {e}")


async def main(topic : str):
    pool = await asyncpg.create_pool(
        host=HOST,
        user=NAME_USER,
        password=PASSWORD,
        database=DATABASE,
        min_size=1,
        max_size=5
    )
    client = aiomqtt.Client(
        hostname=MQTT_ADDRESS,
        port=MQTT_PORT,
        username=MQTT_LOGIN,
        password=MQTT_PASSWORD,
        timeout=5.0
    )

    try:
        async with client as mqtt_client:
            print("[info]: Подключение к брокеру установлено")
            await mqtt_client.subscribe(topic, qos=1)
            print(f"[info]: Ожидаем сообщения в {topic}...")

            async for message in mqtt_client.messages:
                asyncio.create_task(handle_message(message, pool))

    except aiomqtt.MqttError as error:
        print(f"[info]: Сетевая ошибка MQTT: {error}")
    finally:
        if pool:
            await pool.close()
            print("[info]: Пул БД успешно закрыт")

if __name__ == "__main__":
    try:
        asyncio.run(main(MQTT_topic))
    except KeyboardInterrupt:
        print("\n[info]: Воркер остановлен пользователем")