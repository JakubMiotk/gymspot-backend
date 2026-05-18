from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.debt import DebtCreate, DebtOut
from app.services.debt_service import (
    new_debt,
    get_debts,
    get_debt_by_user_id,
    update_debt,
    delete_debt
)

router = APIRouter(tags=["debts"])


# Utworzenie nowego długu
@router.post("/", response_model=DebtOut)
def create_debt(
    debt: DebtCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    debt_data = debt.model_copy(update={"user_id": current_user.id})
    return new_debt(db, debt_data)

# Pobranie wszystkich długów
@router.get("/", response_model=List[DebtOut])
def read_all_debts(
    db: Session = Depends(get_db)):
    return get_debts(db)

# Pobranie długów dla konkretnego użytkownika
@router.get("/user/{user_id}", response_model=List[DebtOut])
def read_debts_for_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return get_debt_by_user_id(db, current_user.id)

# Aktualizacja długu
@router.put("/{debt_id}", response_model=DebtOut)
def update_existing_debt(
    debt_id: int,
    debt_data: DebtCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    debt_payload = debt_data.model_copy(update={"user_id": current_user.id})
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
