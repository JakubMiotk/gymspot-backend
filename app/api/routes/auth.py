from datetime import datetime, timedelta, timezone
from threading import Lock
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserOut
from app.schemas.auth import Token
from app.services.user_service import create_user, get_user_by_username
from app.core.security import verify_password, create_access_token
from app.db.session import get_db

router = APIRouter()


# ============================================================
# LOGIN PROTECTION
# ============================================================

# Po każdym błędnym haśle zwiększamy opóźnienie:
#
# 1 -> 1s
# 2 -> 2s
# 3 -> 4s
# 4 -> 8s
# 5 -> 16s
# 6 -> 32s
# 7+ -> 60s
#
# Dzięki temu nie blokujemy konta całkowicie.
MAX_LOGIN_DELAY = 60

# Limit requestów z jednego IP.
IP_RATE_LIMIT = 20
IP_RATE_WINDOW = timedelta(minutes=1)


_login_lock = Lock()

# username -> liczba ostatnich błędnych logowań
_failed_logins: dict[str, int] = {}

# IP -> timestampy requestów
_ip_requests: dict[str, list[datetime]] = {}


# ============================================================
# HELPERS
# ============================================================

def _normalize_username(username: str) -> str:
    return username.strip().lower()


def _reset_failed_logins(username: str) -> None:
    username = _normalize_username(username)

    with _login_lock:
        _failed_logins.pop(username, None)


def _get_login_delay(username: str) -> int:
    """
    Zwraca aktualne opóźnienie przed kolejną próbą.
    """
    username = _normalize_username(username)

    with _login_lock:
        failed_count = _failed_logins.get(username, 0)

    if failed_count <= 0:
        return 0

    return min(
        2 ** (failed_count - 1),
        MAX_LOGIN_DELAY,
    )


def _register_failed_login(username: str) -> None:
    username = _normalize_username(username)

    with _login_lock:
        current = _failed_logins.get(username, 0)

        _failed_logins[username] = current + 1


def _check_ip_rate_limit(ip: str) -> int | None:
    """
    Zwraca liczbę sekund do ponowienia requestu,
    albo None jeśli request może zostać wykonany.
    """

    now = datetime.now(timezone.utc)

    with _login_lock:
        requests = _ip_requests.get(ip, [])

        # usuwamy stare requesty
        requests = [
            timestamp
            for timestamp in requests
            if now - timestamp < IP_RATE_WINDOW
        ]

        if len(requests) >= IP_RATE_LIMIT:
            oldest = requests[0]

            retry_after = ceil(
                (
                    IP_RATE_WINDOW
                    - (now - oldest)
                ).total_seconds()
            )

            _ip_requests[ip] = requests

            return max(1, retry_after)

        requests.append(now)

        _ip_requests[ip] = requests

        return None


# ============================================================
# REGISTER
# ============================================================

@router.post("/register", response_model=UserOut)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400,
            detail="Nazwa użytkownika jest już zajęta",
        )

    return create_user(
        db,
        user.username,
        user.password,
    )


# ============================================================
# LOGIN
# ============================================================

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # IP RATE LIMIT
    # --------------------------------------------------------

    client_ip = (
        request.client.host
        if request.client
        else "unknown"
    )

    retry_after = _check_ip_rate_limit(client_ip)

    if retry_after is not None:
        raise HTTPException(
            status_code=429,
            detail="Zbyt wiele prób logowania. Spróbuj ponownie później.",
            headers={
                "Retry-After": str(retry_after)
            },
        )

    # --------------------------------------------------------
    # READ REQUEST
    # --------------------------------------------------------

    username: str | None = None
    password: str | None = None

    content_type = request.headers.get(
        "content-type",
        "",
    )

    if "application/x-www-form-urlencoded" in content_type:
        form = await request.form()

        username = form.get("username")
        password = form.get("password")

    else:
        payload = await request.json()

        username = payload.get("username")
        password = payload.get("password")

    if not username or not password:
        raise HTTPException(
            status_code=422,
            detail="Wymagane pola: username i password",
        )

    username = _normalize_username(username)

    # --------------------------------------------------------
    # PROGRESSIVE DELAY
    # --------------------------------------------------------

    delay = _get_login_delay(username)

    if delay > 0:

        raise HTTPException(
            status_code=429,
            detail="Zbyt wiele nieudanych prób logowania. Spróbuj ponownie później.",
            headers={
                "Retry-After": str(delay)
            },
        )

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    db_user = get_user_by_username(
        db,
        username,
    )

    # --------------------------------------------------------
    # VERIFY ACCOUNT
    # --------------------------------------------------------

    if not db_user.active:
        raise HTTPException(
            status_code=403,
            detail="Konto jest nieaktywne.",
        )

    if (
        not db_user
        or not verify_password(
            password,
            db_user.hashed_password,
        )
    ):
        _register_failed_login(username)


        raise HTTPException(
            status_code=401,
            detail="Nieprawidłowy login lub hasło.",
        )


    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    _reset_failed_logins(username)

    token = create_access_token({
        "sub": db_user.username,
        "user_id": db_user.id,
        "role": getattr(
            db_user,
            "role",
            "user",
        ),
    })

    return {
        "access_token": token,
        "token_type": "bearer",
    }
