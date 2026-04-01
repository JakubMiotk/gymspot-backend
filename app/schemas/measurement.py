from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from typing_extensions import Annotated

from app.schemas.measurement_segmental import SegmentalFatCreate, SegmentalFatOut

Decimal41 = Annotated[Decimal, Field(..., max_digits=4, decimal_places=1)]
Decimal31 = Annotated[Decimal, Field(..., max_digits=3, decimal_places=1)]

class MeasurementBase(BaseModel):
    user_id: int
    date: datetime
    weight: Decimal41
    height: int  
    body_fat: Optional[Decimal31] = None
    visceral_fat: Optional[int] = None 
    fat_mass: Optional[Decimal41] = None
    muscle_mass: Optional[Decimal41] = None
    note: Optional[str] = None

class MeasurementCreate(MeasurementBase):
    segmental_fat: Optional[SegmentalFatCreate] = None
    segmental_fat_free: Optional[SegmentalFatCreate] = None

class MeasurementOut(MeasurementBase):
    id: int
    segmental_fat: Optional[SegmentalFatOut] = None
    segmental_fat_free: Optional[SegmentalFatOut] = None

    class Config:
        from_attributes = True
