from fastapi import APIRouter, HTTPException, status
import psycopg2
import os
from dotenv import load_dotenv
from schemas.schem import PricesCreate

load_dotenv()

HOST = os.getenv("HOST")
NAME_USER = os.getenv("NAME_USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
CONNECT = os.getenv("CONNECT")

router_prices = APIRouter(
    prefix="/prices",
    tags=["Всё, что связано с ценами на топливо"]
)


@router_prices.get('/{station_id}')
async def get_prices_of_region(station_id: int, fuel_type: str | None = None):
    connection = None
    try:
        data_res = []
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            if fuel_type:
                cursor.execute(
                    'select p.fuel_type, p.price_per_liter from prices p join station s using(region_id) where s.id = %s and p.fuel_type = %s',
                    (station_id, fuel_type))
            else:
                cursor.execute(
                    'select p.fuel_type, p.price_per_liter from prices p join station s using(region_id) where s.id = %s',
                    (station_id,))
            data_about_prices = cursor.fetchall()
            if not data_about_prices:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Данные по ценам на топливо на АЗС не найдены"
                )
        for records in data_about_prices:
            data_res.append({'fuel_type': records[0], 'prices_per_liter': records[1]})
        return data_res
    except HTTPException:
        raise
    except Exception as e:
        print(f'info: ошибка {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера: не удалось загрузить цены для данного региона"
        )
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')


@router_prices.post("", status_code=status.HTTP_201_CREATED)
async def add_new_price(data_about_new_fuel: PricesCreate):
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('select id from region where region_name=%s', (data_about_new_fuel.region_name,))
            region_id = cursor.fetchone()
            if not region_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Регион '{data_about_new_fuel.region_name}' не найден"
                )
            cursor.execute(
                'insert into prices(region_id, fuel_type, price_per_liter) values (%s, %s, %s) ON CONFLICT (region_id, fuel_type) DO UPDATE SET price_per_liter = EXCLUDED.price_per_liter',
                (region_id[0], data_about_new_fuel.fuel_type, data_about_new_fuel.price_per_liter))
            return {"status": "ok", "code": 201, "fuel_type": data_about_new_fuel.fuel_type,
                    "price_per_liter": data_about_new_fuel.price_per_liter,
                    "region_id": region_id[0]}
    except HTTPException:
        raise
    except Exception as e:
        print(f'info: ошибка {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера: не удалось обновить данные о топливе"
        )
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')

@router_prices.delete("/{region_id}")
async def delete_fuel_price(region_id: int, fuel_type: str):
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                'delete from prices where region_id = %s and fuel_type = %s',
                (str(region_id), fuel_type)
            )
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Цена для топлива {fuel_type} в регионе {region_id} не найдена"
                )
        return {"status": "ok", "code": 200, "message": f"Топливо {fuel_type} удалено из региона {region_id}"}
    except HTTPException:
        raise
    except Exception as e:
        print(f'info: ошибка {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера: не удалось удалить цену на топливо"
        )
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')
