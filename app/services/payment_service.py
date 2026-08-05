import os
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.schemas.payment import PaymentCreate
from app.models.payment import Payment
from app.services.excess_payment_service import upsert_increment_excess_payment
from app.services.debt_service import upsert_increment_debt, consume_debt, consume_all_debt, get_current_debt_value
from app.services.notification_service import send_push_notification_to_user

def new_payment(db: Session, payment_data: PaymentCreate):
    payment = Payment(
        from_user_id=payment_data.from_user_id,
        to_user_id=payment_data.to_user_id,
        date=payment_data.date,
        value=payment_data.value,
        type=payment_data.type
    )

    db.add(payment)

    if payment_data.type == "excess_payment":
        upsert_increment_excess_payment(db, payment_data.from_user_id, payment_data.value)

    if payment_data.type == "debt":
        upsert_increment_debt(db, payment_data.from_user_id, payment_data.value)

    if payment_data.type == "regulacja":
        consume_debt(db, payment_data.from_user_id, payment_data.value)

    db.commit()
    db.refresh(payment)

    formatted_date = payment.date.strftime("%d.%m.%Y")

    if payment.type == "excess_payment":
        try:
            send_push_notification_to_user(
                db,
                user_id=payment.from_user_id,
                title="Nowa nadpłata",
                body=f"Dodano nadpłatę: {payment.value} zł.",
                url=f"/app/profile/{payment.from_user_id}/payments",
            )
        except Exception:
            pass

    if payment.type == "debt":
        try:
            send_push_notification_to_user(
                db,
                user_id=payment.from_user_id,
                title="Nowy dług",
                body=f"Dodano dług: {payment.value} zł.",
                url=f"/app/profile/{payment.from_user_id}/payments",
            )
        except Exception:
            pass

    if payment.type in {"payment", "regulacja"}:
        notification_body = f"Dodano płatność: {payment.value} zł ({formatted_date})."
        recipients = {payment.from_user_id, payment.to_user_id}
        for user_id in recipients:
            try:
                send_push_notification_to_user(
                    db,
                    user_id=user_id,
                    title="Nowa płatność",
                    body=notification_body,
                    url=f"/app/profile/{user_id}/payments",
                )
            except Exception:
                pass

    return payment

def get_payments_by_user_id(db: Session, user_id: int):
    return (
        db.query(Payment)
        .filter((Payment.to_user_id == user_id) | (Payment.from_user_id == user_id))
        .filter(Payment.type != "debt")
        .order_by(desc(func.date(Payment.date)), desc(Payment.id))
        .all()
    )

def get_payments(db: Session):
    return db.query(Payment).order_by(desc(func.date(Payment.date)), desc(Payment.id)).all()

def update_payment(db: Session, payment_id: int, update_data: PaymentCreate):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment  :
        return None
    payment.from_user_id = update_data.from_user_id
    payment.to_user_id = update_data.to_user_id
    payment.date = update_data.date
    payment.value = update_data.value
    payment.type = update_data.type

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
