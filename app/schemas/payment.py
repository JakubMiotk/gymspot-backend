from datetime import datetime
from typing import Literal
from pydantic import BaseModel

class PaymentBase(BaseModel):
    from_user_id: int
    to_user_id: int 
    date: datetime
    value: int
    type: Literal[
        "payment",
        "excess_payment",
        "debt",
        "regulacja"
    ] = "payment"

class PaymentCreate(PaymentBase):
    pass

class PaymentOut(PaymentBase):
    id: int

    class Config:
        from_attributes = True