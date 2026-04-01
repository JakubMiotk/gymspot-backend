from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password

def create_user(db: Session, username: str, password: str, role="user"):
    hashed = get_password_hash(password)
    user = User(
        username=username,
        hashed_password=hashed,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_users(db: Session):
    return db.query(User).all()

def change_user_password(db: Session, user: User, old_password: str, new_password: str):
    # Weryfikacja starego hasła
    if not verify_password(old_password, user.hashed_password):
        return False

    # Hashowanie nowego hasła
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return True