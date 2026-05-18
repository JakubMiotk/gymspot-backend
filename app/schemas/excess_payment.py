from datetime import datetime
from typing import Literal
from pydantic import BaseModel

class ExcessPaymentBase(BaseModel):
    user_id: int 
    value: int

class ExcessPaymentCreate(ExcessPaymentBase):
    pass

class ExcessPaymentOut(ExcessPaymentBase):
    id: int

    class Config:
        from_attributes = True