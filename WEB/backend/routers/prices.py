from fastapi import APIRouter, HTTPException, status, Depends
from dotenv import load_dotenv
from schemas.schem import PricesCreate
from database import get_db_pool
import asyncpg

load_dotenv()

router_prices = APIRouter(
    prefix="/prices",
    tags=["Всё, что связано с ценами на топливо"]
)


@router_prices.get('/{station_id}')
async def get_prices_of_region(station_id: int, fuel_type: str | None = None,
                               pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        if fuel_type:
            query = 'select p.fuel_type, p.price_per_liter from prices p join station s using(region_id) where s.id = $1 and p.fuel_type = $2'
            data_about_prices = await connection.fetch(query, station_id, fuel_type)
        else:
            query = 'select p.fuel_type, p.price_per_liter from prices p join station s using(region_id) where s.id = $1'
            data_about_prices = await connection.fetch(query, station_id)
        if not data_about_prices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Данные по ценам на топливо на АЗС не найдены"
            )
        return [dict(price) for price in data_about_prices]


@router_prices.post("", status_code=status.HTTP_201_CREATED)
async def add_new_price(data_about_new_fuel: PricesCreate, pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = 'select id from region where region_name=$1'
        region_id = await connection.fetchval(query, data_about_new_fuel.region_name)
        if not region_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Регион '{data_about_new_fuel.region_name}' не найден"
            )
        query = 'insert into prices(region_id, fuel_type, price_per_liter) values ($1, $2, $3) ON CONFLICT (region_id, fuel_type) DO UPDATE SET price_per_liter = EXCLUDED.price_per_liter'
        await connection.execute(query, region_id, data_about_new_fuel.fuel_type, data_about_new_fuel.price_per_liter)
        return {"region_id": region_id, "fuel_type": data_about_new_fuel.fuel_type,
                "price_per_liter": data_about_new_fuel.price_per_liter,
                }


@router_prices.delete("/{region_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fuel_price(region_id: int, fuel_type: str, pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = 'delete from prices where region_id = $1 and fuel_type = $2'
        status_str = await connection.execute(query, region_id, fuel_type)
        # status_str вернет строку вида "DELETE 1" или "DELETE 0"
        # Парсим количество удаленных строк:
        deleted_count = int(status_str.split()[-1])
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Цена для топлива '{fuel_type}' в регионе {region_id} не найдена",
            )
        return None