from pydantic import BaseModel, Field

class StationCreate(BaseModel):
    region: str = Field(title="Название региона или области")
    adress: str = Field(title="Адрес АЗС")
    rating: int = Field(title="Рейтинг заправки", default=0)