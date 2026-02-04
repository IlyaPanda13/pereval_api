from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime


class User(BaseModel):
    fam: str = Field(..., description="Фамилия")
    name: str = Field(..., description="Имя")
    otc: Optional[str] = Field(None, description="Отчество")
    email: EmailStr = Field(..., description="Email")
    phone: str = Field(..., description="Телефон")


class Coordinates(BaseModel):
    latitude: str = Field(..., description="Широта")
    longitude: str = Field(..., description="Долгота")
    height: str = Field(..., description="Высота")


class Level(BaseModel):
    winter: Optional[str] = Field("", description="Зима")
    summer: Optional[str] = Field("", description="Лето")
    autumn: Optional[str] = Field("", description="Осень")
    spring: Optional[str] = Field("", description="Весна")


class Image(BaseModel):
    data: str = Field(..., description="Изображение в base64")
    title: str = Field(..., description="Название изображения")


class PerevalData(BaseModel):
    beauty_title: Optional[str] = Field("", description="Красивое название")
    title: str = Field(..., description="Название перевала")
    other_titles: Optional[str] = Field("", description="Другие названия")
    connect: Optional[str] = Field("", description="Что соединяет")
    add_time: str = Field(..., description="Время добавления")

    user: User
    coords: Coordinates
    level: Level
    images: List[Image]

    @validator('add_time')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
            return v
        except ValueError:
            raise ValueError('Неверный формат даты. Используйте: YYYY-MM-DD HH:MM:SS')