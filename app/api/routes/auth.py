from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import Token
from app.services.user_service import create_user, get_user_by_username
from app.core.security import verify_password, create_access_token
from app.db.session import get_db

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Nazwa użytkownika jest już zajęta")
    return create_user(db, user.username, user.password)

@router.post("/login", response_model=Token)
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Nieprawidłowy login lub hasło")
    
    token = create_access_token({
        "sub": db_user.username,
        "user_id": db_user.id,
        "role": getattr(db_user, "role", "user")
    })

    return {"access_token": token, "token_type": "bearer"}
