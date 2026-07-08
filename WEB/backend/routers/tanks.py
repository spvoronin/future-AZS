from fastapi import APIRouter
import psycopg2
import os
from dotenv import load_dotenv
from schemas.schem import TankCreate

load_dotenv()

HOST = os.getenv("HOST")
NAME_USER = os.getenv("NAME_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
CONNECT = os.getenv("CONNECT")

router_tanks = APIRouter(
    prefix="/tanks",
    tags=["Всё, что связано с цистернами"]
)


@router_tanks.get("/station/{station_id}")
async def get_station_tanks(station_id: int):
    connection = None
    try:
        data_res = []
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('''
                SELECT id, tank_number, compartment_number, fuel_type, max_capacity, current_liters, temperature
                FROM tanks 
                WHERE station_id = %s
            ''', (station_id,))

            tanks_data = cursor.fetchall()
            if not tanks_data:
                return {"status": "error", "message": "Цистерны для этой АЗС не найдены"}

        for row in tanks_data:
            max_capacity = row[4]
            current_liters = row[5]
            fill_percent = round((current_liters / max_capacity) * 100, 2) if max_capacity > 0 else 0
            data_res.append({
                "tank_id": row[0],
                "tank_number": row[1],
                "compartment_number": row[2],
                "fuel_type": row[3],
                "max_capacity_liters": max_capacity,
                "current_liters": current_liters,
                "fill_percentage": f"{fill_percent}%",
                "temperature": row[6]
            })
        return data_res
    except Exception as e:
        print(f"info: ошибка {e}")
        return {"status": "error", "message": "Не удалось получить данные резервуаров"}
    finally:
        if connection:
            connection.close()


@router_tanks.put("/{tank_id}/refill")
async def refill_tank(tank_id: int, data: float):
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_liters, max_capacity FROM tanks WHERE id = %s", (tank_id,))
            tank = cursor.fetchone()
            if not tank:
                return {"status": "error", "message": "Цистерна не найдена"}

            current, max_cap = tank[0], tank[1]
            new_volume = current + data

            if new_volume > max_cap:
                return {
                    "status": "error",
                    "message": f"Невозможно залить {data}л. В цистерне доступно только {max_cap - current}л."
                }

            cursor.execute(
                "UPDATE tanks SET current_liters = %s WHERE id = %s",
                (new_volume, tank_id)
            )

        return {
            "status": "ok",
            "message": f"Цистерна {tank_id} успешно пополнена",
            "current_liters": new_volume
        }
    except Exception as e:
        print(f"info: ошибка {e}")
        return {"status": "error", "message": "Ошибка при обновлении данных цистерны"}
    finally:
        if connection:
            connection.close()

@router_tanks.post("")
async def create_tank(data: TankCreate):
    if data.current_liters > data.max_capacity:
        return {
            "status": "error",
            "message": f"Начальный объем ({data.current_liters}л) не может превышать макс. емкость ({data.max_capacity}л)"
        }
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM station WHERE id = %s", (data.station_id,))
            if not cursor.fetchone():
                return {"status": "error", "message": f"АЗС с id {data.station_id} не существует"}

            cursor.execute('''
                    INSERT INTO tanks (station_id, tank_number, compartment_number, fuel_type, max_capacity, current_liters, temperature)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (station_id, tank_number, compartment_number) 
                    DO UPDATE SET 
                        fuel_type = EXCLUDED.fuel_type, 
                        max_capacity = EXCLUDED.max_capacity,
                        current_liters = EXCLUDED.current_liters,
                        temperature = EXCLUDED.temperature
                    RETURNING id
                ''', (data.station_id, data.tank_number, data.compartment_number, data.fuel_type,
                      data.max_capacity, data.current_liters, data.temperature))

            new_tank_id = cursor.fetchone()[0]

        return {
            "status": "ok",
            "code": 201,
            "message": f"Резервуар/отсек успешно создан",
            "tank_id": new_tank_id
        }
    except Exception as e:
        print(f"info: ошибка {e}")
        return {"status": "error", "message": "Не удалось зарегистрировать цистерну"}
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')