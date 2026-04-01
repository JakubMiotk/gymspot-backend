import os
from sqlalchemy.orm import Session
from app.schemas.payment import PaymentCreate
from app.models.payment import Payment

def new_payment(db: Session, payment_data: PaymentCreate):
    payment = Payment(
        from_user_id=payment_data.from_user_id,
        to_user_id=payment_data.to_user_id,
        date=payment_data.date,
        value=payment_data.value
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

def get_payments_by_user_id(db: Session, user_id: int):
    return db.query(Payment).filter((Payment.to_user_id == user_id) | (Payment.from_user_id == user_id)).all()

def get_payments(db: Session):
    return db.query(Payment).all()

def update_payment(db: Session, payment_id: int, update_data: PaymentCreate):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment  :
        return None
    payment.from_user_id = update_data.from_user_id
    payment.to_user_id = update_data.to_user_id
    payment.date = update_data.date
    payment.value = update_data.value

    db.commit()
    db.refresh(payment)
    return payment


def delete_payment(db: Session, payment_id: int):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment:
        db.delete(payment)
        db.commit()
        return True
    return False
