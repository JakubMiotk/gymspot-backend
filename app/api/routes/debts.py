from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_person, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.person import Person
from app.schemas.debt import DebtCreate, DebtOut
from app.services.debt_service import (
    new_debt,
    get_debts,
    get_debt_by_person_id,
    update_debt,
    delete_debt
)

router = APIRouter(tags=["debts"])


# Utworzenie nowego długu
@router.post("/", response_model=DebtOut)
def create_debt(
    debt: DebtCreate,
    db: Session = Depends(get_db),
    current_person: Person = Depends(get_current_person)):
    debt_data = debt.model_copy(update={"person_id": current_person.id})
    return new_debt(db, debt_data)

# Pobranie wszystkich długów
@router.get("/", response_model=List[DebtOut])
def read_all_debts(
    db: Session = Depends(get_db)):
    return get_debts(db)

# Pobranie długów dla konkretnego użytkownika
@router.get("/person/{person_id}", response_model=List[DebtOut])
def read_debts_for_person(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_person: Person = Depends(get_current_person)):
    requested_person_id = person_id if current_user.role == "trainer" else current_person.id
    return get_debt_by_person_id(db, requested_person_id)

# Aktualizacja długu
@router.put("/{debt_id}", response_model=DebtOut)
def update_existing_debt(
    debt_id: int,
    debt_data: DebtCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    current_person = db.query(Person).filter(Person.user_id == current_user.id).first()
    if current_person is None:
        raise HTTPException(status_code=409, detail="Konto nie ma powiązanego profilu osoby")
    debt_payload = debt_data.model_copy(update={"person_id": current_person.id})
    debt = update_debt(db, debt_id, debt_payload)

    if not debt:
        raise HTTPException(status_code=404, detail="Nie znaleziono długu")

    return debt

# Usunięcie długu
@router.delete("/{debt_id}")
def remove_debt(
    debt_id: int,
    db: Session = Depends(get_db)):
    success = delete_debt(db, debt_id)

    if not success:
        raise HTTPException(status_code=404, detail="Nie znaleziono długu")

    return {"msg": "Dług został usunięty"}
