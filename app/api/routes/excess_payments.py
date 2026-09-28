from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_person, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.person import Person
from app.schemas.excess_payment import ExcessPaymentCreate, ExcessPaymentOut
from app.services.excess_payment_service import (
    new_excess_payment,
    get_excess_payments,
    get_excess_payment_by_person_id,
    update_excess_payment,
    delete_excess_payment
)

router = APIRouter(tags=["excess_payments"])


# Utworzenie nowej nadpłaty
@router.post("/", response_model=ExcessPaymentOut)
def create_excess_payment(
    payment: ExcessPaymentCreate,
    db: Session = Depends(get_db),
    current_person: Person = Depends(get_current_person)):
    payment_data = payment.model_copy(update={"person_id": current_person.id})
    return new_excess_payment(db, payment_data)

# Pobranie wszystkich nadpłat
@router.get("/", response_model=List[ExcessPaymentOut])
def read_all_excess_payments(
    db: Session = Depends(get_db)):
    return get_excess_payments(db)

# Pobranie nadpłat dla konkretnego użytkownika
@router.get("/person/{person_id}", response_model=List[ExcessPaymentOut])
def read_excess_payments_for_person(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_person: Person = Depends(get_current_person)):
    requested_person_id = person_id if current_user.role == "trainer" else current_person.id
    return get_excess_payment_by_person_id(db, requested_person_id)

# Aktualizacja nadpłaty
@router.put("/{payment_id}", response_model=ExcessPaymentOut)
def update_existing_payment(
    payment_id: int,
    payment_data: ExcessPaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    current_person = db.query(Person).filter(Person.user_id == current_user.id).first()
    if current_person is None:
        raise HTTPException(status_code=409, detail="Konto nie ma powiązanego profilu osoby")
    payment_payload = payment_data.model_copy(update={"person_id": current_person.id})
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
