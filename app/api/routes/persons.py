import os
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from typing import List
from app.core.deps import get_current_person, get_current_user
from app.schemas.person import PersonBase, PersonOut
from app.services.person_service import activate_person, deactivate_person, get_person_by_user_id, link_person, new_person, get_persons, delete_person, update_person, update_avatar
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.person import Person
from app.models.user import User


UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(tags=["persons"])


# Pobierz wszystkie osoby
@router.get("/", response_model=List[PersonOut])
def read_persons(db: Session = Depends(get_db)):
    return get_persons(db)

# Profil osoby powiązanej z kontem logowania
@router.get("/me", response_model=PersonOut)
def read_my_person(current_person: Person = Depends(get_current_person)):
    return current_person

# Pobierz osobę po person.id
@router.get("/{person_id}", response_model=PersonOut)
def read_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Nie znaleziono osoby")
    return person

# Utworzenie profilu osoby; trener może utworzyć profil niepowiązany z kontem.
@router.post("/", response_model=PersonOut)
def register_user(
    person: PersonBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "trainer":
        if person.user_id not in (None, current_user.id):
            raise HTTPException(status_code=403, detail="Nie można przypisać profilu do innego konta")
        if person.user_id == current_user.id and db.query(Person).filter(Person.user_id == current_user.id).first():
            raise HTTPException(status_code=409, detail="Konto ma już powiązany profil")
        person_data = person.model_copy(update={"user_id": person.user_id})
    else:
        existing_person = db.query(Person).filter(Person.user_id == current_user.id).first()
        if existing_person:
            raise HTTPException(status_code=409, detail="Konto ma już powiązany profil")
        person_data = person.model_copy(update={"user_id": current_user.id})
    return new_person(db, person_data)

# Aktualizacja osoby po person.id
@router.put("/{person_id}", response_model=PersonOut)
def change_person(
    person_id: int,
    person_update: PersonBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_person: Person = Depends(get_current_person),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person or (current_user.role != "trainer" and person.id != current_person.id):
        raise HTTPException(status_code=404, detail="Nie znaleziono osoby")

    person_data = person_update.model_copy(update={"user_id": person.user_id})
    updated_person = update_person(db, person_id, person_data)
    if not updated_person:
        raise HTTPException(status_code=500, detail="Nie udało się zaktualizować osoby")
    return updated_person

# Usunięcie osoby po person.id
@router.delete("/{person_id}")
def remove_person(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person or (current_user.role != "trainer" and person.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Nie znaleziono osoby")
    delete_person(db, person_id)
    return {"msg": "Osoba została pomyślnie usunięta"}

#Dodanie awataru

@router.post("/avatar/{person_id}", response_model=PersonOut)
async def upload_avatar(
    person_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    current_person: Person = Depends(get_current_person),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person or (current_user.role != "trainer" and person.id != current_person.id):
        raise HTTPException(status_code=404, detail="Nie znaleziono osoby")
    # Sprawdzenie typu
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="To nie jest obraz")

    # Bezpieczne rozszerzenie
    ext = file.filename.split(".")[-1].lower()
    if ext not in ("jpg", "jpeg", "png", "gif", "webp"):
        raise HTTPException(status_code=400, detail="Nieobsługiwany format pliku")

    # Generowanie nazwy
    filename = f"person_{person_id}_{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)

    # Zapis pliku
    try:
        with open(path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nie udało się zapisać pliku: {e}")

    # Aktualizacja awatara w bazie
    updated_avatar = update_avatar(db, person_id=person_id, filename=filename)
    if not updated_avatar:
        if os.path.exists(path):
            os.remove(path)
        raise HTTPException(status_code=500, detail="Nie udało się zaktualizować awatara w bazie")

    return updated_avatar

@router.post("/deactivate/{person_id}")
def deactivate_person_endpoint(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person or (current_user.role != "trainer" and person.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Nie znaleziono osoby")
    deactivate_person(db, person_id)
    return {"msg": "Osoba została dezaktywowana"}
    
@router.post("/activate/{person_id}")
def activate_person_endpoint(
    person_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person or (current_user.role != "trainer" and person.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Nie znaleziono osoby")
    activate_person(db, person_id)
    return {"msg": "Osoba została aktywowana"}

@router.post("/link/{person_id}")
def link_person_endpoint(
    person_id: int,
    linked_person_id: int | None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person or (current_user.role != "trainer" and person.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Nie znaleziono osoby")
    linked_person = link_person(db, user_id=current_user.id, linked_person_id=linked_person_id)
    if not linked_person:
        raise HTTPException(status_code=500, detail="Nie udało się powiązać osoby")
    return linked_person