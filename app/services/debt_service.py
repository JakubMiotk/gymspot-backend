import os
from sqlalchemy.orm import Session
from app.schemas.debt import DebtCreate
from app.models.debts import Debt

def upsert_increment_debt(db: Session, user_id: int, amount: int):
    debt = db.query(Debt).filter(Debt.user_id == user_id).first()
    if debt:
        debt.value += amount
    else:
        debt = Debt(user_id=user_id, value=amount)
        db.add(debt)
    db.flush()
    return debt


def consume_debt(db: Session, user_id: int, amount: int) -> bool:
    """Zmniejsza dług o podaną kwotę. Zwraca True jeśli dług wystarczył, False wpp."""
    debt = db.query(Debt).filter(Debt.user_id == user_id).first()
    if not debt or debt.value < amount:
        return False
    debt.value -= amount
    db.flush()
    return True


def consume_all_debt(db: Session, user_id: int) -> int:
    """Zeruje cały dług i zwraca skonsumowaną kwotę."""
    debt = db.query(Debt).filter(Debt.user_id == user_id).first()
    if not debt or debt.value <= 0:
        return 0
    consumed = debt.value
    debt.value = 0
    db.flush()
    return consumed


def get_current_debt_value(db: Session, user_id: int) -> int:
    debt = db.query(Debt).filter(Debt.user_id == user_id).first()
    return debt.value if debt else 0


def new_debt(db: Session, payment_data: DebtCreate):
    debt = Debt(
        user_id=payment_data.user_id,
        value=payment_data.value
    )
    db.add(debt)
    db.commit()
    db.refresh(debt)
    return debt

def get_debt_by_user_id(db: Session, user_id: int):
    return db.query(Debt).filter(Debt.user_id == user_id).all()

def get_debts(db: Session):
    return db.query(Debt).all()

def update_debt(db: Session, user_id: int, update_data: DebtCreate):
    debt = db.query(Debt).filter(Debt.user_id == user_id).first()
    if not debt:
        return None
    debt.user_id = update_data.user_id
    debt.value = update_data.value

    db.commit()
    db.refresh(debt)
    return debt



def delete_debt(db: Session, debt_id: int):
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if debt:
        db.delete(debt)
        db.commit()
        return True
    return False
