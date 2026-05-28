from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.schemas.auth import Token
from app.services.user_service import create_user, get_user_by_username
from app.core.security import verify_password, create_access_token
from app.db.session import get_db

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Nazwa użytkownika jest już zajęta")
    return create_user(db, user.username, user.password, user.role)

@router.post("/login", response_model=Token)
async def login(request: Request, db: Session = Depends(get_db)):
    username: str | None = None
    password: str | None = None

    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
    else:
        payload = await request.json()
        username = payload.get("username")
        password = payload.get("password")

    if not username or not password:
        raise HTTPException(status_code=422, detail="Wymagane pola: username i password")

    db_user = get_user_by_username(db, username)
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Nieprawidłowy login lub hasło")
    
    token = create_access_token({
        "sub": db_user.username,
        "user_id": db_user.id,
        "role": getattr(db_user, "role", "user")
    })

    return {"access_token": token, "token_type": "bearer"}
