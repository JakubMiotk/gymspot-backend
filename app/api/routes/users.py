from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_current_user
from app.schemas.user import ChangePassword, UserOut, UserCreate
from app.services.user_service import change_user_password, create_user, get_user_by_username, get_user_by_id, get_users
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User

router = APIRouter(tags=["users"])

# Pobierz aktualnie zalogowanego użytkownika
@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

# Pobierz wszystkich użytkowników
@router.get("/", response_model=List[UserOut])
def read_users(db: Session = Depends(get_db)):
    return get_users(db)

# Pobierz użytkownika po ID
@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Nie znaleziono użytkownika")
    return user

# Rejestracja użytkownika
@router.post("/", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Nazwa użytkownika jest już zajęta")

    return create_user(db, user.username, user.password, user.role)


@router.post("/change-password")
def change_password(
    passwords: ChangePassword,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    success = change_user_password(db, current_user, passwords.old_password, passwords.new_password)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Stare hasło jest niepoprawne"
        )
    return {"msg": "Hasło zostało pomyślnie zaktualizowane"}