from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.payment import PaymentCreate, PaymentOut
from app.services.payment_service import (
    new_payment,
    get_payments,
    get_payments_by_user_id,
    update_payment,
    delete_payment
)

router = APIRouter(tags=["payments"])


# Utworzenie nowej płatności
@router.post("/", response_model=PaymentOut)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db)):
    return new_payment(db, payment)

# Pobranie wszystkich płatności
@router.get("/", response_model=List[PaymentOut])
def read_all_payments(
    db: Session = Depends(get_db)):
    return get_payments(db)

# Pobranie płatności dla konkretnego użytkownika
@router.get("/user/{user_id}", response_model=List[PaymentOut])
def read_payments_for_user(
    user_id: int,
    db: Session = Depends(get_db)):
    return get_payments_by_user_id(db, user_id)


# Aktualizacja płatności
@router.put("/{payment_id}", response_model=PaymentOut)
def update_existing_payment(
    payment_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db)):
    payment = update_payment(db, payment_id, payment_data)

    if not payment:
        raise HTTPException(status_code=404, detail="Nie znaleziono płatności")

    return payment

# Usunięcie płatności
@router.delete("/{payment_id}")
def remove_payment(
    payment_id: int,
    db: Session = Depends(get_db)):
    success = delete_payment(db, payment_id)

    if not success:
        raise HTTPException(status_code=404, detail="Nie znaleziono płatności")

    return {"msg": "Płatność została usunięta"}
