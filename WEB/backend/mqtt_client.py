import aiomqtt
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

load_dotenv()

@asynccontextmanager
async def lifespan_mqtt() -> AsyncIterator[aiomqtt.Client]:
    client = aiomqtt.Client(
        hostname=os.getenv("MQTT_ADDRESS"),
        port=int(os.getenv("MQTT_PORT")),
        username=os.getenv("MQTT_LOGIN"),
        password=os.getenv("MQTT_PASSWORD"),
        timeout=5.0
    )
    async with client:
        print("INFO:     Async MQTT client connected successfully")
        yield client

    print("INFO:     Async MQTT client disconnected")