from fastapi import APIRouter
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST")
NAME_USER = os.getenv("NAME_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
CONNECT = os.getenv("CONNECT")

UUID = os.getenv("UUID")

router_sensor = APIRouter(
    prefix="/sensors",
    tags=["Всё, что связано с датчиками"]
)


@router_sensor.get("")
async def get_vol_from_sensor():
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                'select uuid, electric_current, flame, gas, ambient_humidity, ambient_temperature, tank_temperature, water_level from sensors where uuid=%s order by id desc limit 1',
                (UUID,))
            data_about_sensors = cursor.fetchone()
            if data_about_sensors is None:
                return {"status": "error", "message": "Данные не найдены"}
            data_res = {
                "uuid": data_about_sensors[0],
                "electric_current": data_about_sensors[1],
                "flame": data_about_sensors[2],
                "gas": data_about_sensors[3],
                "ambient_humidity": data_about_sensors[4],
                "ambient_temperature": data_about_sensors[5],
                "tank_temperature": data_about_sensors[6],
                "water_level": data_about_sensors[7]
            }
        return data_res
    except Exception as e:
        print(f'info: ошибка {e}')
        return {"status": "error", "message": "Не удалось получить данные с датчиков"}
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')