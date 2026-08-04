from fastapi import APIRouter, HTTPException, status as http_status, Depends
from schemas.schem import StationCreate
from database import get_db_pool
import asyncpg

router_stations = APIRouter(
    prefix="/stations",
    tags=["Всё, что связано с самой АЗС"]
)


@router_stations.get("")
async def get_all_stations(pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = '''SELECT
                        station.id AS id,
                        region.region_name AS region,
                        address,
                        rating
                   FROM station
                   LEFT JOIN region ON station.region_id = region.id'''
        data_all_stations = await connection.fetch(query)
        return [dict(record) for record in data_all_stations]


@router_stations.get("/{station_id}")
async def get_one_station(station_id: int,
                          pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = '''SELECT
                        station.id AS id,
                        region.region_name AS region,
                        address,
                        rating
                   FROM station
                   LEFT JOIN region ON station.region_id = region.id
                   WHERE station.id=$1'''
        data_one_station = await connection.fetchrow(query, station_id)
        if not data_one_station:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Станция не найдена"
            )
        return dict(data_one_station)


@router_stations.post("", status_code=http_status.HTTP_201_CREATED)
async def add_new_station(data_about_new_station: StationCreate,
                          pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        async with connection.transaction():
            query = '''
                INSERT INTO region (region_name)
                VALUES ($1)
                ON CONFLICT (region_name) DO UPDATE 
                    SET region_name = EXCLUDED.region_name
                RETURNING id
            '''
            region_id = await connection.fetchval(query, data_about_new_station.region)

            query = '''INSERT INTO station(address, rating, region_id)
                       VALUES
                            ($1, $2, $3)
                       RETURNING id'''
            new_id = await connection.fetchval(query, data_about_new_station.address, data_about_new_station.rating, region_id)
            return {
                "status": "ok",
                "code": 201,
                "new_id": new_id,
                "region_id": region_id,
                "address": data_about_new_station.address,
                "rating": data_about_new_station.rating
            }


@router_stations.put("/{station_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def update_data_about_station(station_id: int,
                                    region: str | None = None,
                                    address: str | None = None,
                                    pool: asyncpg.Pool = Depends(get_db_pool)):
    update_data = {}
    async with pool.acquire() as connection:
        async with connection.transaction():
            query = '''SELECT
                            id
                       FROM station
                       WHERE id=$1'''
            res = await connection.fetchval(query, station_id)

            if not res:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Станция не найдена"
                )

            if region is not None:
                query = '''
                    INSERT INTO region (region_name)
                    VALUES ($1)
                    ON CONFLICT (region_name) DO UPDATE 
                        SET region_name = EXCLUDED.region_name
                    RETURNING id
                '''
                region_id = await connection.fetchval(query, region)
                update_data["region_id"] = region_id

            if address is not None:
                update_data["address"] = address

            fields, values = [], []
            idx = 1

            for key, val in update_data.items():
                fields.append(f"{key} = ${idx}")
                values.append(val)
                idx += 1

            if not fields:
                return None

            query = f"UPDATE station SET {', '.join(fields)} WHERE id=${idx}::int"
            status_str = await connection.execute(query, *values, station_id)

            return None


@router_stations.delete("/{station_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_station(station_id: int,
                         pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = '''DELETE FROM station
                   WHERE id=$1'''
        status_str = await connection.execute(query, station_id)
        deleted_count = int(status_str.split()[-1])
        if deleted_count == 0:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Станция не найдена"
            )
        return None


@router_stations.get("/{station_id}/pumps")
async def data_about_pumps_on_stations(station_id: int,
                                       pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = '''SELECT
                        id
                   FROM station
                   WHERE id=$1'''
        res = await connection.fetchval(query, station_id)

        if not res:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Станция не найдена"
            )
        query = '''SELECT
                        id,
                        pump_number,
                        status,
                        is_active
                    FROM pumps
                    WHERE station_id=$1'''
        data_all_pumps_on_one_station = await connection.fetch(query, station_id)
        return [dict(record) for record in data_all_pumps_on_one_station]
