from datetime import datetime
from pydantic import BaseModel

class PaymentBase(BaseModel):
    from_user_id: int
    to_user_id: int 
    date: datetime
    value: int

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int

    class Config:
        from_attributes = True