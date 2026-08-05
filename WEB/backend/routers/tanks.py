from fastapi import APIRouter, HTTPException, status as http_status, Depends
from schemas.schem import TankCreate
from database import get_db_pool
import asyncpg


router_tanks = APIRouter(
    prefix="/tanks",
    tags=["Всё, что связано с цистернами"]
)

@router_tanks.get("/station/{station_id}")
async def get_station_tanks(station_id: int,
                            pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = '''SELECT
                        id
                   FROM station
                   WHERE id = $1'''
        station_exists = await connection.fetchval(query, station_id)
        if not station_exists:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Станция не найдена"
            )

        data_res = []
        query = '''
                    SELECT 
                        id AS tank_id,
                        tank_number,
                        compartment_number,
                        fuel_type,
                        max_capacity,
                        current_liters,
                        temperature
                    FROM tanks 
                    WHERE station_id = $1
                '''
        tanks_data = await connection.fetch(query, station_id)
        for row in tanks_data:
            max_capacity = row["max_capacity"] or 0
            current_liters = row["current_liters"] or 0
            fill_percent = round((current_liters / max_capacity) * 100, 2) if max_capacity > 0 else 0
            data_res.append({
                "tank_id": row['tank_id'],
                "tank_number": row['tank_number'],
                "compartment_number": row['compartment_number'],
                "fuel_type": row['fuel_type'],
                "max_capacity_liters": max_capacity,
                "current_liters": current_liters,
                "fill_percentage": f"{fill_percent}%",
                "temperature": row['temperature']
            })
        return data_res


@router_tanks.put("/{tank_id}/refill")
async def refill_tank(tank_id: int,
                      data: float,
                      pool: asyncpg.Pool = Depends(get_db_pool)):
    if data <= 0:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Объем пополнения должен быть больше 0"
        )
    async with pool.acquire() as connection:
        async with connection.transaction():
            query = '''SELECT
                             current_liters,
                             max_capacity 
                        FROM tanks 
                        WHERE id = $1 
                        FOR UPDATE'''
            tank = await connection.fetchrow(query, tank_id)
            if not tank:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Цистерна не найдена"
                )

            current = tank["current_liters"] or 0.0
            max_cap = tank["max_capacity"] or 0.0
            new_volume = current + data

            if new_volume > max_cap:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Невозможно залить {data}л. В цистерне доступно только {max_cap - current}л."
                )

            query = ''' UPDATE tanks 
                        SET current_liters = $1 
                        WHERE id = $2
            '''
            await connection.execute(query, new_volume, tank_id)

        return {
            "status": "ok",
            "message": f"Цистерна {tank_id} успешно пополнена",
            "current_liters": new_volume
        }


@router_tanks.post("", status_code=http_status.HTTP_201_CREATED)
async def create_tank(data: TankCreate,
                      pool: asyncpg.Pool = Depends(get_db_pool)):
    if data.current_liters > data.max_capacity:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Объем не может превышать макс. емкость"
        )
    async with pool.acquire() as connection:
        async with connection.transaction():
            query = '''SELECT
                            id 
                       FROM station
                       WHERE id = $1'''
            station_exists = await connection.fetchval(query, data.station_id)
            if not station_exists:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"АЗС с id {data.station_id} не существует"
                )
            query = '''INSERT INTO tanks (
                    station_id, 
                    tank_number, 
                    compartment_number, 
                    fuel_type, 
                    max_capacity, 
                    current_liters, 
                    temperature
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (station_id, tank_number, compartment_number) 
                DO UPDATE SET 
                    fuel_type = EXCLUDED.fuel_type, 
                    max_capacity = EXCLUDED.max_capacity,
                    current_liters = EXCLUDED.current_liters,
                    temperature = EXCLUDED.temperature
                RETURNING id
            '''

            new_tank_id = await connection.fetchval(
                query,
                data.station_id,
                data.tank_number,
                data.compartment_number,
                data.fuel_type,
                data.max_capacity,
                data.current_liters,
                data.temperature
            )

        return {
            "status": "ok",
            "message": f"Резервуар/отсек успешно создан",
            "tank_id": new_tank_id
        }