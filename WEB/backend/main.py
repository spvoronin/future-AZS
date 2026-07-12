from fastapi import FastAPI
from routers.pumps import router_pumps
from routers.stations import router_stations
from routers.users import router_users
from routers.prices import router_prices
from routers.tanks import router_tanks
from routers.transactions import router_transactions
from routers.sensors import router_sensor
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "https://smartaf.ru",
    "http://localhost:5173", # для локальной разработки, если нужно
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(router_stations)
app.include_router(router_users)
app.include_router(router_pumps)
app.include_router(router_prices)
app.include_router(router_tanks)
app.include_router(router_transactions)
app.include_router(router_sensor)