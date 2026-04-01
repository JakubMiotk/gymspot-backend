from datetime import date
from pydantic import BaseModel

class PersonBase(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    gender: str
    height: float
    weight: float
    date_of_birth: date
    city: str
    avatar: str | None = None

class PersonOut(PersonBase):
    id: int
    avatar: str | None = None

    class Config:
        from_attributes = True