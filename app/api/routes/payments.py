from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_person, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.person import Person
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentOut
from app.services.payment_service import (
    new_payment,
    get_payments,
    get_payments_by_person_id,
    update_payment,
    delete_payment
)

router = APIRouter(tags=["payments"])


# Utworzenie nowej płatności
@router.post("/", response_model=PaymentOut)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_person: Person = Depends(get_current_person)):
    payment_data = payment.model_copy(update={"from_person_id": current_person.id})
    return new_payment(db, payment_data)

# Pobranie wszystkich płatności
@router.get("/", response_model=List[PaymentOut])
def read_all_payments(
    db: Session = Depends(get_db)):
    return get_payments(db)

# Pobranie płatności dla konkretnego użytkownika
@router.get("/person/{person_id}", response_model=List[PaymentOut])
def read_payments_for_person(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_person: Person = Depends(get_current_person)):
    requested_person_id = person_id if current_user.role == "trainer" else current_person.id
    return get_payments_by_person_id(db, requested_person_id)


# Aktualizacja płatności
@router.put("/{payment_id}", response_model=PaymentOut)
def update_existing_payment(
    payment_id: int,
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    current_person = db.query(Person).filter(Person.user_id == current_user.id).first()
    if current_person is None:
        raise HTTPException(status_code=409, detail="Konto nie ma powiązanego profilu osoby")
    existing = db.query(Payment).filter(Payment.id == payment_id).first()
    if existing is None or (current_user.role != "trainer" and existing.from_person_id != current_person.id):
        raise HTTPException(status_code=404, detail="Nie znaleziono płatności")
    payment_payload = payment_data.model_copy(update={"from_person_id": current_person.id})
    payment = update_payment(db, payment_id, payment_payload)

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
