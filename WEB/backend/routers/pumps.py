from fastapi import APIRouter, HTTPException, status
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
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute('select id, station_id, pump_number, status, is_active from pumps where id=%s',
                           (id_pump,))
            data_one_pump = cursor.fetchone()
            if data_one_pump is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"ТРК с ID {id_pump} не найдена"
                )
        data_res = {"id": data_one_pump[0], "station_id": data_one_pump[1], "pump_number": data_one_pump[2],
                    "status": data_one_pump[3], "is_active": data_one_pump[4]}
        return data_res
    except HTTPException:
        raise
    except Exception as e:
        print(f'info: ошибка {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера при поиске ТРК"
        )
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')


@router_pumps.post("", status_code=status.HTTP_201_CREATED)
async def add_new_pump(data_about_new_pump: PumpCreate):
    connection = None
    try:
        connection = psycopg2.connect(host=HOST, user=NAME_USER, password=PASSWORD, database=DATABASE)
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(
                'insert into pumps(station_id, pump_number, status, is_active) values (%s, %s, %s, %s) returning id', (
                    data_about_new_pump.station_id, data_about_new_pump.pump_number,
                    data_about_new_pump.status,
                    data_about_new_pump.is_active))
            new_id = cursor.fetchone()[0]
        return {"status_res": "ok", "code": 201, "new_id": new_id, "station_id": data_about_new_pump.station_id,
                "pump_number": data_about_new_pump.pump_number, "status": data_about_new_pump.status,
                "is_active": data_about_new_pump.is_active}
    except HTTPException:
        raise
    except Exception as e:
        print(f'info: ошибка {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать ТРК"
        )
    finally:
        if connection:
            connection.close()
            print('info: коннект закрыт')


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
async def delete_pump(pump_id : int):
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
