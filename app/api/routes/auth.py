from datetime import datetime, timedelta, timezone
from math import ceil
from threading import Lock

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserOut, UserLogin
from app.schemas.auth import Token
from app.services.user_service import create_user, get_user_by_username
from app.core.security import verify_password, create_access_token
from app.db.session import get_db

router = APIRouter()

MAX_FAILED_LOGINS = 3
LOCKOUT_MINUTES = 10

_login_attempts_lock = Lock()
_login_attempts: dict[str, dict[str, datetime | int]] = {}


def _reset_login_attempts(username: str) -> None:
    with _login_attempts_lock:
        _login_attempts.pop(username, None)


def _is_locked(username: str) -> int | None:
    now = datetime.now(timezone.utc)

    with _login_attempts_lock:
        state = _login_attempts.get(username)
        if not state:
            return None

        locked_until = state.get("locked_until")
        if not isinstance(locked_until, datetime):
            return None

        if locked_until <= now:
            _login_attempts.pop(username, None)
            return None

        seconds_left = (locked_until - now).total_seconds()
        return max(1, ceil(seconds_left / 60))


def _register_failed_attempt(username: str) -> tuple[bool, int]:
    now = datetime.now(timezone.utc)

    with _login_attempts_lock:
        state = _login_attempts.get(username)
        failed_count = 0

        if state and isinstance(state.get("failed_count"), int):
            failed_count = int(state["failed_count"])

        failed_count += 1

        if failed_count >= MAX_FAILED_LOGINS:
            locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
            _login_attempts[username] = {
                "failed_count": 0,
                "locked_until": locked_until,
            }
            return True, LOCKOUT_MINUTES

        _login_attempts[username] = {
            "failed_count": failed_count,
        }
        return False, failed_count

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

    minutes_left = _is_locked(username)
    if minutes_left is not None:
        raise HTTPException(
            status_code=423,
            detail=f"Konto zablokowane po wielu nieudanych próbach. Spróbuj ponownie za {minutes_left} min.",
        )

    db_user = get_user_by_username(db, username)
    if not db_user or not verify_password(password, db_user.hashed_password):
        is_now_locked, value = _register_failed_attempt(username)
        if is_now_locked:
            raise HTTPException(
                status_code=423,
                detail=f"Konto zostało zablokowane na {value} min po 3 błędnych próbach logowania.",
            )

        attempts_left = MAX_FAILED_LOGINS - value
        raise HTTPException(
            status_code=400,
            detail=f"Nieprawidłowy login lub hasło. Pozostało prób: {attempts_left}.",
        )

    _reset_login_attempts(username)
    
    token = create_access_token({
        "sub": db_user.username,
        "user_id": db_user.id,
        "role": getattr(db_user, "role", "user")
    })

    return {"access_token": token, "token_type": "bearer"}
