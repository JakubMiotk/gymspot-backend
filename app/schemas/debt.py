from datetime import datetime
from typing import Literal
from pydantic import BaseModel

class DebtBase(BaseModel):
    user_id: int 
    value: int

class DebtCreate(DebtBase):
    pass

class DebtOut(DebtBase):
    id: int

    class Config:
        from_attributes = True