from fastapi import FastAPI
from routers.pumps import router_pumps
from routers.stations import router_stations
from routers.users import router_users
from routers.prices import router_prices
from routers.tanks import router_tanks
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_stations)
app.include_router(router_users)
app.include_router(router_pumps)
app.include_router(router_prices)
app.include_router(router_tanks)