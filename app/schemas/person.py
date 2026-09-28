from datetime import date
from pydantic import BaseModel

class PersonBase(BaseModel):
    user_id: int | None = None
    first_name: str
    last_name: str
    gender: str
    height: float | None = None
    weight: float | None = None
    date_of_birth: date | None = None
    city: str | None = None
    avatar: str | None = None

class PersonOut(PersonBase):
    id: int
    avatar: str | None = None

    class Config:
        allow_population_by_field_name = True
        orm_mode = True