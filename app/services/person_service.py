import os
from sqlalchemy.orm import Session
from app.models.person import Person
from app.core.security import get_password_hash, verify_password
from app.schemas.person import PersonBase

def new_person(db: Session, person_data: PersonBase):
    person = Person(
        first_name=person_data.first_name,
        last_name=person_data.last_name,
        gender=person_data.gender,
        height=person_data.height,
        weight=person_data.weight,
        date_of_birth=person_data.date_of_birth,
        city=person_data.city,
        user_id=person_data.user_id 
    )

    db.add(person)
    db.commit()
    db.refresh(person)
    return person

def get_person_by_user_id(db: Session, user_id: int):
    return db.query(Person).filter(Person.user_id == user_id).first()

def get_persons(db: Session):
    return db.query(Person).all()

def update_person(db: Session, person_id: int, update_data: PersonBase):
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        return None
    person.first_name = update_data.first_name
    person.last_name = update_data.last_name
    person.gender = update_data.gender
    person.height = update_data.height
    person.weight = update_data.weight
    person.date_of_birth = update_data.date_of_birth
    person.city = update_data.city

    db.commit()
    db.refresh(person)
    return person


def delete_person(db: Session, person_id: int):
    person = db.query(Person).filter(Person.id == person_id).first()
    if person:
        db.delete(person)
        db.commit()
        return True
    return False

def update_avatar(db: Session, user_id: int, filename: str):
    person = db.query(Person).filter(Person.id == user_id).first()
    if not person:
        return None

    # Usuwanie starego pliku, jeśli istnieje
    if person.avatar:
        old_path = os.path.join("uploads/avatars", os.path.basename(person.avatar))
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                print(f"Nie udało się usunąć starego awatara: {e}")

    # Aktualizacja nowego awatara
    person.avatar = f"/avatars/{filename}"
    db.commit()
    db.refresh(person)
    return person
    