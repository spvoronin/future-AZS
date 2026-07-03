from fastapi import APIRouter
import psycopg2
import os
from dotenv import load_dotenv
from schemas.schem import StationCreate


load_dotenv()

HOST = os.getenv("HOST")
NAME_USER = os.getenv("NAME_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
CONNECT = os.getenv("CONNECT")

router_stations = APIRouter(
    prefix="/stations",
    tags=["Всё, что связано с самой АЗС"]
)

@router_stations.get("")
async def get_all_stations():
    try:
        data_res = []
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('select * from station order by id desc')
            data_all_stations = cursor.fetchall()
        connection.close()
        print('info: коннект закрыт')
        for records in data_all_stations:
            data_res.append({"id": records[0], "region": records[1], "adress": records[2], "rating" : records[3]})
        return data_res
    except Exception as e:
        print(f'info: ошибка {e}')
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')

@router_stations.get("/{station_id}")
async def get_one_station(station_id : int):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('select * from station where id=%s', (str(station_id), ))
            data_one_station = cursor.fetchone()
            if data_one_station is None:
                return {"status": "error", "message": "Станция не найдена"}
        data_res = {"id": data_one_station[0], "region": data_one_station[1], "adress": data_one_station[2], "rating" : data_one_station[3]}
        return data_res
    except Exception as e:
        print(f'info: ошибка {e}')
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')

@router_stations.post("")
async def add_new_station(data_about_new_station : StationCreate):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('insert into station(region, adress, rating) values (%s, %s, %s)', (data_about_new_station.region, data_about_new_station.adress, str(data_about_new_station.rating)))
            cursor.execute('select id from station order by id desc')
            new_id = cursor.fetchone()[0]
        connection.close()
        print('info: коннект закрыт')
        return {"status": "ok", "code" : 201, "new_id" : new_id, "region" : data_about_new_station.region, "address" : data_about_new_station.adress, "rating" : data_about_new_station.rating}
    except Exception as e:
        print(f'info: ошибка {e}')
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')

@router_stations.put("/{id}")
async def update_data_about_station(id : int = 0, region : str | None = None, adress : str | None = None):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            if region:
                cursor.execute("update station set region=%s where id=%s", (region, str(id)))
            if adress:
                cursor.execute("update station set adress=%s where id=%s", (adress, str(id)))
        return {"status": "ok", "code" : 204}
    except Exception as e:
        print(f'info: ошибка {e}')
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')

@router_stations.delete("/{id}")
async def data_data_about_station(id : int):
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("delete from station where id=%s", (str(id),))
        return {"status": "ok", "code" : 204}
    except Exception as e:
        print(f'info: ошибка {e}')
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')