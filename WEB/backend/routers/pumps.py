from fastapi import APIRouter, HTTPException, status as http_status, Depends
from schemas.schem import PumpCreate
from database import get_db_pool
import asyncpg

router_pumps = APIRouter(
    prefix="/pumps",
    tags=["Всё, что связано с ТРК"]
)

@router_pumps.get("/{id_pump}")
async def get_one_pump(id_pump: int, pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:

        query = 'select id, station_id, pump_number, status, is_active from pumps where id=$1'
        data_one_pump = await connection.fetchrow(query, id_pump)

        if not data_one_pump:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"ТРК с ID {id_pump} не найдена"
            )

        return dict(data_one_pump)


@router_pumps.post("", status_code=http_status.HTTP_201_CREATED)
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


@router_pumps.put("/{pump_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def update_data_about_pump(
                                 pump_id: int,
                                 station_id: int | None = None,
                                 pump_number: int | None = None,
                                 status: str | None = None,
                                 is_active: bool | None = None,
                                 pool: asyncpg.Pool = Depends(get_db_pool)
                                ):
    update_data = {
        "station_id": station_id,
        "pump_number": pump_number,
        "status": status,
        "is_active": is_active
    }
    fields, values = [], []
    idx = 1

    for key, val in update_data.items():
        if val is not None:
            fields.append(f"{key} = ${idx}")
            values.append(val)
            idx += 1

    async with pool.acquire() as connection:
        exists = await connection.fetchval("SELECT id FROM pumps WHERE id = $1", pump_id)
        if not exists:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="ТРК не найдена"
            )

        if not fields:
            return None

        query = f"UPDATE pumps SET {', '.join(fields)} WHERE id=${idx}::int"
        await connection.execute(query, *values, pump_id)

        return None



@router_pumps.delete("/{pump_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_pump(pump_id: int, pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = "DELETE FROM pumps WHERE id=$1"
        status_str = await connection.execute(query, pump_id)
        deleted_count = int(status_str.split()[-1])
        if deleted_count == 0:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="ТРК не найдена"
            )
        return None
