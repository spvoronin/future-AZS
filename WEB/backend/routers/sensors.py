from fastapi import APIRouter, Depends, HTTPException, status as http_status, Request
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from dependencies import verify_admin, get_current_user
from database import get_db_pool
import asyncpg
import aiomqtt

load_dotenv()

UUID = os.getenv("UUID")

router_sensor = APIRouter(
    prefix="/sensors",
    tags=["Всё, что связано с датчиками"]
)

@router_sensor.get("")
async def get_vol_from_sensor(user: dict = Depends(get_current_user), pool: asyncpg.Pool = Depends(get_db_pool)):
    async with pool.acquire() as connection:
        query = 'select uuid, electric_current, flame, gas, ambient_humidity, ambient_temperature, tank_temperature, water_level, voltage from sensors where uuid=$1 order by id desc limit 1'
        data_about_sensors = await connection.fetchrow(query, UUID)
        if not data_about_sensors:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Данные не найдены"
            )
    return dict(data_about_sensors)

@router_sensor.post("/pumps/{pumps_id}")
async def vkl_pump(pumps_id : int,
                   request: Request,
                   admin_user: dict = Depends(verify_admin)):

    mqtt_client: aiomqtt.Client = getattr(request.app.state, "mqtt_client", None)

    if mqtt_client is None:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="MQTT-клиент не инициализирован"
        )

    MQTT_topic = f"BV/SAF/{pumps_id}"

    try:
        await mqtt_client.publish(MQTT_topic, payload="change", qos=1)
        return {"status": "ok", "message": f"Команда успешно отправлена в {MQTT_topic}"}
    except aiomqtt.MqttError as error:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка отправки MQTT команды: {str(error)}"
        )