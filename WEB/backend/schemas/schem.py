from pydantic import BaseModel, Field

class StationCreate(BaseModel):
    region: str = Field(title="Название региона или области")
    adress: str = Field(title="Адрес АЗС")
    rating: int = Field(title="Рейтинг заправки", default=0)

class UserCreate(BaseModel):
    phone: str = Field(title="Номер телефона")
    email: str = Field(title="Почта")
    password_hash: str = Field(title="Пароль")
    first_name: str = Field(title="Имя")
    number_of_car: str = Field(title="Номер машины")