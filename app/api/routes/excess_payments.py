from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.excess_payment import ExcessPaymentCreate, ExcessPaymentOut
from app.services.excess_payment_service import (
    new_excess_payment,
    get_excess_payments,
    get_excess_payment_by_user_id,
    update_excess_payment,
    delete_excess_payment
)

router = APIRouter(tags=["excess_payments"])


# Utworzenie nowej nadpłaty
@router.post("/", response_model=ExcessPaymentOut)
def create_excess_payment(
    payment: ExcessPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    payment_data = payment.model_copy(update={"user_id": current_user.id})
    return new_excess_payment(db, payment_data)

# Pobranie wszystkich nadpłat
@router.get("/", response_model=List[ExcessPaymentOut])
def read_all_excess_payments(
    db: Session = Depends(get_db)):
    return get_excess_payments(db)

# Pobranie nadpłat dla konkretnego użytkownika
@router.get("/user/{user_id}", response_model=List[ExcessPaymentOut])
def read_excess_payments_for_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return get_excess_payment_by_user_id(db, current_user.id)

# Aktualizacja nadpłaty
@router.put("/{payment_id}", response_model=ExcessPaymentOut)
def update_existing_payment(
    payment_id: int,
    payment_data: ExcessPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    payment_payload = payment_data.model_copy(update={"user_id": current_user.id})
    payment = update_excess_payment(db, payment_id, payment_payload)

    if not payment:
        raise HTTPException(status_code=404, detail="Nie znaleziono nadpłaty")

    return payment

# Usunięcie nadpłaty
@router.delete("/{payment_id}")
def remove_payment(
    payment_id: int,
    db: Session = Depends(get_db)):
    success = delete_excess_payment(db, payment_id)

    if not success:
        raise HTTPException(status_code=404, detail="Nie znaleziono nadpłaty")

    return {"msg": "Nadpłata została usunięta"}
