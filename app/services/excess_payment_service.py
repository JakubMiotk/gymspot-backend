import os
from sqlalchemy.orm import Session
from app.schemas.excess_payment import ExcessPaymentCreate
from app.models.excess_payments import ExcessPayment 


def upsert_increment_excess_payment(db: Session, user_id: int, amount: int):
    excess_payment = db.query(ExcessPayment).filter(ExcessPayment.user_id == user_id).first()

    if excess_payment:
        excess_payment.value += amount
        return excess_payment

    excess_payment = ExcessPayment(
        user_id=user_id,
        value=amount
    )
    db.add(excess_payment)
    return excess_payment

def consume_excess_payment(db: Session, user_id: int, amount: int):
    excess_payment = db.query(ExcessPayment).filter(ExcessPayment.user_id == user_id).first()

    if not excess_payment or excess_payment.value < amount:
        return False

    excess_payment.value -= amount
    return True

def consume_all_excess(db: Session, user_id: int) -> int:
    """Zero out the user's excess and return the amount consumed."""
    excess_payment = db.query(ExcessPayment).filter(ExcessPayment.user_id == user_id).first()
    if not excess_payment or excess_payment.value <= 0:
        return 0
    consumed = excess_payment.value
    excess_payment.value = 0
    return consumed

def new_excess_payment(db: Session, payment_data: ExcessPaymentCreate):
    excess_payment = ExcessPayment(
        user_id=payment_data.user_id,
        value=payment_data.value
    )
    db.add(excess_payment)
    db.commit()
    db.refresh(excess_payment)
    return excess_payment

def get_excess_payment_by_user_id(db: Session, user_id: int):
    return db.query(ExcessPayment).filter(ExcessPayment.user_id == user_id).all()

def get_excess_payments(db: Session):
    return db.query(ExcessPayment).all()

def update_excess_payment(db: Session, excess_payment_id: int, update_data: ExcessPaymentCreate):
    excess_payment = db.query(ExcessPayment).filter(ExcessPayment.id == excess_payment_id).first()
    if not excess_payment:
        return None
    excess_payment.user_id = update_data.user_id
    excess_payment.value = update_data.value

    db.commit()
    db.refresh(excess_payment)
    return excess_payment



def delete_excess_payment(db: Session, excess_payment_id: int):
    excess_payment = db.query(ExcessPayment).filter(ExcessPayment.id == excess_payment_id).first()
    if excess_payment:
        db.delete(excess_payment)
        db.commit()
        return True
    return False
