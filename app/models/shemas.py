from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class RegistrationUserShema(BaseModel):
    telegram_id: Optional[int] = Field(None, description="Telegram ID пользователя")
    first_name: Optional[str] = Field(None, description="Имя")
    last_name: Optional[str] = Field(None, description="Фамилия")
    username: Optional[str] = Field(None, description="Никнейм")

class UserCreate(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None

class UserShema(BaseModel):
    telegram_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    joined_date: datetime
    habits: Optional[List['HabitShemaOUT']] = []

class UserShemaOUT(UserShema):
    id: int


class HabitShema(BaseModel):
    title: str
    frequency: Optional[str]
    goal_days: Optional[int]
    owner_id: Optional[int] = 0
    trackings: Optional[List['TrackingShemaOUT']] = []

class HabitShemaOUT(HabitShema):
    id: int


class TrackingShema(BaseModel):
    date: datetime
    was_performed: bool
    habit_id: int

class TrackingShemaOUT(TrackingShema):
    id: int