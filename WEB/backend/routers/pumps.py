from fastapi import APIRouter
import psycopg2
import os
from dotenv import load_dotenv
from schemas.schem import PumpCreate

load_dotenv()

HOST = os.getenv("HOST")
NAME_USER = os.getenv("NAME_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
CONNECT = os.getenv("CONNECT")

router_pumps = APIRouter(
    prefix="/pumps",
    tags=["Всё, что связано с ТРК"]
)


@router_pumps.get("/{id_pump}")
async def get_one_pump(id_pump: int):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('select id, station_id, pump_number, status, is_active from pumps where id=%s',
                           (str(id_pump),))
            data_one_pump = cursor.fetchone()
            if data_one_pump is None:
                return {"status": "error", "message": "ТРК не найдена", "code": 404}
        data_res = {"id": data_one_pump[0], "station_id": data_one_pump[1], "pump_number": data_one_pump[2],
                    "status": data_one_pump[3], "is_active": data_one_pump[4]}
        return data_res
    except Exception as e:
        print(f'info: ошибка {e}')
        return {"status": "error", "message": "Ошибка сервера при поиске ТРК"}
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')


@router_pumps.post("")
async def add_new_pump(data_about_new_pump: PumpCreate):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                'insert into pumps(station_id, pump_number, status, is_active) values (%s, %s, %s, %s) returning id', (
                    str(data_about_new_pump.station_id), str(data_about_new_pump.pump_number),
                    data_about_new_pump.status,
                    str(data_about_new_pump.is_active)))
            new_id = cursor.fetchone()[0]
        return {"status_res": "ok", "code": 201, "new_id": new_id, "station_id": data_about_new_pump.station_id,
                "pump_number": data_about_new_pump.pump_number, "status": data_about_new_pump.status,
                "is_active": data_about_new_pump.is_active}
    except Exception as e:
        print(f'info: ошибка {e}')
        return {"status": "error", "message": "Не удалось создать ТРК"}
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')


@router_pumps.put("/{pump_id}")
async def update_data_about_pump(pump_id: int = 0, station_id: int | None = None, pump_number: int | None = None,
                                 status: str | None = None, is_active: bool | None = None):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            if station_id:
                cursor.execute("update pumps set station_id=%s where id=%s", (station_id, str(pump_id)))
            if pump_number:
                cursor.execute("update pumps set pump_number=%s where id=%s", (pump_number, str(pump_id)))
            if status:
                cursor.execute("update pumps set status=%s where id=%s", (status, str(pump_id)))
            if is_active is not None:
                cursor.execute("update pumps set is_active=%s where id=%s", (is_active, str(pump_id)))
        return {"status": "ok", "code": 204}
    except Exception as e:
        print(f'info: ошибка {e}')
        return {"status": "error", "message": "Не удалось обновить данные ТРК"}
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')

@router_pumps.delete("/{pump_id}")
async def delete_pump(pump_id : int):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("delete from pumps where id=%s", (str(pump_id),))
        return {"status": "ok", "code" : 204}
    except Exception as e:
        print(f'info: ошибка {e}')
        return {"status": "error", "message": "Не удалось удалить ТРК"}
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')
