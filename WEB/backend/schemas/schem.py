from pydantic import BaseModel, Field

class StationCreate(BaseModel):
    region: str = Field(title="Название региона или области")
    adress: str = Field(title="Адрес АЗС")
    rating: int = Field(title="Рейтинг заправки", default=0)

class UserLogin(BaseModel):
    email: str = Field(title="Почта")
    password_hash: str = Field(title="Пароль")

class UserCreate(UserLogin):
    phone: str = Field(title="Номер телефона")
    first_name: str = Field(title="Имя")
    number_of_car: str = Field(title="Номер машины")

class PumpCreate(BaseModel):
    station_id : int = Field(title="Айди АЗС, на которой стоит ТРК")
    pump_number : int = Field(title="Номер ТРК на АЗС")
    status : str = Field(Field="Статус")
    is_active : bool = Field(title="Доступность")

class PricesCreate(BaseModel):
    region_name : str = Field(title="Название региона")
    fuel_type : str = Field(title="Вид топлива")
    price_per_liter : float = Field(title="Цена за литр топлива")

class TankCreate(BaseModel):
    station_id: int
    tank_number: int
    compartment_number: int
    fuel_type: str
    max_capacity: float = Field(..., gt=0)
    current_liters: float = Field(..., ge=0)
    temperature: float = Field(20.0, description="Текущая температура топлива")

class TransactionCreate(BaseModel):
    user_id: int
    pump_id: int
    fuel_type: str
    requested_liters: float = Field(..., gt=0, description="Количество заказываемых литров")

