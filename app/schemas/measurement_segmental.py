from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Annotated

# Definiujemy typ z walidacją
Decimal41 = Annotated[Decimal, Field(ge=0, le=999.9, max_digits=4, decimal_places=1)]

class SegmentalFatBase(BaseModel):
    left_arm: Decimal41
    right_arm: Decimal41
    trunk: Decimal41
    left_leg: Decimal41
    right_leg: Decimal41

class SegmentalFatCreate(SegmentalFatBase):
    pass 

class SegmentalFatOut(SegmentalFatBase):
    id: int
    measurement_id: int

    class Config:
        from_attributes = True