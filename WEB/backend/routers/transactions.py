from fastapi import APIRouter, HTTPException, status as http_status, Depends
from schemas.schem import TransactionCreate
from database import get_db_pool
import asyncpg


router_transactions = APIRouter(
    prefix="/transactions",
    tags=["Всё, что связано с транзакциями и заказами"]
)

@router_transactions.post("")
async def create_transaction(data: TransactionCreate,
                             pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        async with connection.transaction():
            # 1-й запрос: Получаем сразу информацию о ТРК, АЗС и цене топлива
            query_info = '''
                SELECT 
                    p.is_active, 
                    p.status AS pump_status, 
                    p.station_id, 
                    pr.price_per_liter
                FROM pumps p
                JOIN station s ON p.station_id = s.id
                LEFT JOIN prices pr ON pr.region_id = s.region_id AND pr.fuel_type = $2
                WHERE p.id = $1
            '''
            info_row = await connection.fetchrow(query_info, data.pump_id, data.fuel_type)

            # Проверки колонок и цен
            if not info_row:
                raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Указанная ТРК не найдена")
            if not info_row["is_active"]:
                raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST,
                                    detail="ТРК временно отключена на обслуживание")
            if info_row["pump_status"] != 'idle':
                raise HTTPException(status_code=http_status.HTTP_409_CONFLICT,
                                    detail="На этой ТРК прямо сейчас идет налив или произошел сбой")
            if info_row["price_per_liter"] is None:
                raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND,
                                    detail=f"Топливо {data.fuel_type} не продается в данном регионе")

            station_id = info_row["station_id"]
            price_per_liter = float(info_row["price_per_liter"])

            # 2-й запрос: Блокируем цистерну с нужным топливом
            query_tank = '''
                SELECT id, current_liters 
                FROM tanks 
                WHERE station_id = $1 AND fuel_type = $2 AND current_liters >= $3
                LIMIT 1
                FOR UPDATE
            '''
            tank_row = await connection.fetchrow(query_tank, station_id, data.fuel_type, data.requested_liters)

            if not tank_row:
                raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST,
                                    detail="На АЗС недостаточно топлива для вашего заказа")

            tank_id = tank_row["id"]
            current_tank_liters = float(tank_row["current_liters"])
            new_tank_volume = current_tank_liters - data.requested_liters

            # 3-й запрос: Одновременное обновление остатка в цистерне, смены статуса ТРК и создание транзакции
            query_execute_order = '''
                WITH update_tank AS (
                    UPDATE tanks 
                    SET current_liters = $1 
                    WHERE id = $2
                ),
                update_pump AS (
                    UPDATE pumps 
                    SET status = 'dispensing' 
                    WHERE id = $3
                )
                INSERT INTO transactions (pump_id, fuel_type, requested_liters, status, user_id)
                VALUES ($3, $4, $5, 'progress', $6)
                RETURNING id;
            '''

            transaction_id = await connection.fetchval(
                query_execute_order,
                new_tank_volume,
                tank_id,
                data.pump_id,
                data.fuel_type,
                data.requested_liters,
                data.user_id
            )

            total_cost = round(data.requested_liters * price_per_liter, 2)

        return {
            "status": "ok",
            "code": 201,
            "transaction_id": transaction_id,
            "message": "Заказ оформлен, налив запущен",
            "price_per_liter": price_per_liter,
            "total_cost_rub": total_cost
        }