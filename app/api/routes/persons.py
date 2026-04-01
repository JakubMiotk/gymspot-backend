import os
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_current_user
from app.schemas.person import PersonBase, PersonOut
from app.services.person_service import get_person_by_user_id, new_person, get_persons, delete_person, update_person, update_avatar
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.person import Person


UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(tags=["persons"])


# Pobierz wszystkie osoby
@router.get("/", response_model=List[PersonOut])
def read_persons(db: Session = Depends(get_db)):
    return get_persons(db)

# Pobierz osobe po user_id
@router.get("/{user_id}", response_model=PersonOut)
def read_person(user_id: int, db: Session = Depends(get_db)):
    person = get_person_by_user_id(db, user_id)
    if not person:
        raise HTTPException(status_code=404, detail="Nie znaleziono osoby")
    return person

# Stworzenie użytkownika
@router.post("/", response_model=PersonOut)
def register_user(person: PersonBase, db: Session = Depends(get_db)):
    print(person)
    return new_person(db, person)

# Aktualizacja osoby po user_id
@router.put("/{user_id}", response_model=PersonOut)
def change_person(user_id: int, person_update: PersonBase, db: Session = Depends(get_db)):
    # najpierw pobieramy osobę
    person = get_person_by_user_id(db, user_id)
    if not person:
        raise HTTPException(status_code=404, detail="Nie znaleziono osoby")

    # aktualizujemy osobę
    updated_person = update_person(db, person.id, person_update)
    if not updated_person:
        raise HTTPException(status_code=500, detail="Nie udało się zaktualizować osoby")
    return updated_person

# Usunięcie osoby
@router.delete("/{user_id}")
def remove_person(user_id: int, db: Session = Depends(get_db)):
    person = get_person_by_user_id(db, user_id)
    if not person:
        raise HTTPException(status_code=404, detail="Nie znaleziono osoby")
    return {"msg": "Osoba została pomyślnie usunięta"}

#Dodanie awataru

@router.post("/avatar/{user_id}", response_model=PersonOut)
async def upload_avatar(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Sprawdzenie typu
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="To nie jest obraz")

    # Bezpieczne rozszerzenie
    ext = file.filename.split(".")[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
        raise HTTPException(status_code=400, detail="Nieobsługiwany format pliku")

    # Generowanie nazwy
    filename = f"user_{user_id}_{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    # Zapis pliku
    try:
        with open(path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nie udało się zapisać pliku: {e}")

    # Aktualizacja awatara w bazie
    updated_avatar = update_avatar(db, user_id=user_id, filename=filename)
    if not updated_avatar:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=500, detail="Nie udało się zaktualizować awatara w bazie")

    return updated_avatar
