from fastapi import APIRouter, HTTPException, status, Depends
import psycopg2
import os
from dotenv import load_dotenv
from schemas.schem import PumpCreate
from database import get_db_pool
import asyncpg

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
async def get_one_pump(id_pump: int, pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = 'select id, station_id, pump_number, status, is_active from pumps where id=$1 limit 1'
        data_one_pump = await connection.fetchrow(query, id_pump)
        if not data_one_pump:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ТРК с ID {id_pump} не найдена"
            )
        return dict(data_one_pump)


@router_pumps.post("", status_code=status.HTTP_201_CREATED)
async def add_new_pump(data_about_new_pump: PumpCreate, pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = 'insert into pumps(station_id, pump_number, status, is_active) values ($1, $2, $3, $4) returning id'
        new_id = await connection.fetchval(
            query,
            data_about_new_pump.station_id,
            data_about_new_pump.pump_number,
            data_about_new_pump.status,
            data_about_new_pump.is_active
        )
    return {"status_res": "ok", "code": 201, "new_id": new_id, **data_about_new_pump.model_dump()}


@router_pumps.put("/{pump_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_data_about_pump(pump_id: int, station_id: int | None = None, pump_number: int | None = None,
                                 status: str | None = None, is_active: bool | None = None):
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            fields, values = [], []
            if station_id is not None: fields.append("station_id=%s"); values.append(station_id)
            if pump_number is not None: fields.append("pump_number=%s"); values.append(pump_number)
            if status is not None: fields.append("status=%s"); values.append(status)
            if is_active is not None: fields.append("is_active=%s"); values.append(is_active)

            if not fields:
                return None

            values.append(pump_id)

            with connection.cursor() as cursor:
                query = f"UPDATE pumps SET {', '.join(fields)} WHERE id=%s"
                cursor.execute(query, tuple(values))

                if cursor.rowcount == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="ТРК не найдена"
                    )

            return None
    except HTTPException:
        raise
    except Exception as e:
        print(f'info: ошибка {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера: не удалось обновить данные ТРК"
        )
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')


@router_pumps.delete("/{pump_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pump(pump_id: int):
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM pumps WHERE id=%s", (pump_id,))

            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="ТРК не найдена"
                )
        return None
    except HTTPException:
        raise
    except Exception as e:
        print(f'info: ошибка {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении ТРК"
        )
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')
