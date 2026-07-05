from fastapi import APIRouter
import psycopg2
import os
from dotenv import load_dotenv
from schemas.schem import TransactionCreate

load_dotenv()

HOST = os.getenv("HOST")
NAME_USER = os.getenv("NAME_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")

router_transactions = APIRouter(
    prefix="/transactions",
    tags=["Всё, что связано с транзакциями и заказами"]
)




@router_transactions.post("")
async def create_transaction(data: TransactionCreate):
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = False
        with connection.cursor() as cursor:

            cursor.execute('''
                SELECT p.is_active, p.status, p.station_id, s.region_id 
                FROM pumps p
                JOIN station s ON p.station_id = s.id
                WHERE p.id = %s
            ''', (data.pump_id,))
            pump_row = cursor.fetchone()

            if not pump_row:
                return {"status": "error", "message": "Указанная ТРК не найдена"}
            if not pump_row[0]:
                return {"status": "error", "message": "ТРК временно отключена на обслуживание"}
            if pump_row[1] != 'idle':
                return {"status": "error", "message": "На этой ТРК прямо сейчас идет налив или произошел сбой"}

            station_id = pump_row[2]
            region_id = pump_row[3]

            cursor.execute('''
                SELECT price_per_liter FROM prices 
                WHERE region_id = %s AND fuel_type = %s
            ''', (region_id, data.fuel_type))
            price_row = cursor.fetchone()
            if not price_row:
                return {"status": "error", "message": f"Топливо {data.fuel_type} не продается в данном регионе"}

            price_per_liter = price_row[0]

            cursor.execute('''
                SELECT id, current_liters FROM tanks 
                WHERE station_id = %s AND fuel_type = %s AND current_liters >= %s
                LIMIT 1
                FOR UPDATE
            ''', (station_id, data.fuel_type, data.requested_liters))
            tank_row = cursor.fetchone()

            if not tank_row:
                return {"status": "error", "message": "На АЗС недостаточно топлива для вашего заказа"}

            tank_id = tank_row[0]
            current_tank_liters = tank_row[1]

            new_tank_volume = int(current_tank_liters - data.requested_liters)
            cursor.execute('UPDATE tanks SET current_liters = %s WHERE id = %s', (new_tank_volume, tank_id))

            cursor.execute("UPDATE pumps SET status = 'dispensing' WHERE id = %s", (data.pump_id,))

            cursor.execute('''
                INSERT INTO transactions (pump_id, fuel_type, requested_liters, status, user_id)
                VALUES (%s, %s, %s, 'progress', %s) RETURNING id
            ''', (data.pump_id, data.fuel_type, data.requested_liters, data.user_id))

            transaction_id = cursor.fetchone()[0]
            total_cost = round(data.requested_liters * price_per_liter, 2)

            connection.commit()

        return {
            "status": "ok",
            "code": 201,
            "transaction_id": transaction_id,
            "message": "Заказ оформлен, налив запущен",
            "price_per_liter": price_per_liter,
            "total_cost_rub": total_cost
        }

    except Exception as e:
        if connection:
            connection.rollback()
        print(f"info: ошибка транзакции {e}")
        return {"status": "error", "message": "Ошибка сервера при формировании заказа"}
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')