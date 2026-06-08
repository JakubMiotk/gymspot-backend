from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.exercise import ExerciseCreate, ExerciseOut
from app.services.exercise_service import (
    new_exercise,
    get_exercises,
    get_exercise_by_id,
    update_exercise,
    delete_exercise,
    get_exercise_name
)

router = APIRouter(tags=["exercises"])


# Utworzenie nowego ćwiczenia
@router.post("/", response_model=ExerciseOut)
def create_exercise(
    exercise: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    exercise_data = exercise.model_copy(update={"from_user_id": current_user.id})
    return new_exercise(db, exercise_data)

# Pobranie wszystkich ćwiczeń
@router.get("/", response_model=List[ExerciseOut])
def read_all_exercises(
    db: Session = Depends(get_db)):
    return get_exercises(db)

# Pobranie ćwiczenia po ID
@router.get("/id/{exercise_id}", response_model=ExerciseOut)
def read_exercise_by_id(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    exercise = get_exercise_by_id(db, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Nie znaleziono ćwiczenia")
    return exercise

# Aktualizacja ćwiczenia
@router.put("/{exercise_id}", response_model=ExerciseOut)
def update_existing_exercise(
    exercise_id: int,
    exercise_data: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    exercise_payload = exercise_data.model_copy(update={"from_user_id": current_user.id})
    exercise = update_exercise(db, exercise_id, exercise_payload)

    if not exercise:
        raise HTTPException(status_code=404, detail="Nie znaleziono ćwiczenia")

    return exercise

# Usunięcie ćwiczenia
@router.delete("/{exercise_id}")
def remove_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    success = delete_exercise(db, exercise_id)

    if not success:
        raise HTTPException(status_code=404, detail="Nie znaleziono ćwiczenia")

    return {"msg": "Ćwiczenie zostało usunięte"}

#Pobranie ćwiczenia po nazwie
@router.get("/name/{exercise_name}", response_model=ExerciseOut)
def read_exercise_by_name(
    exercise_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    exercise = get_exercise_name(db, exercise_name)
    if not exercise:
        raise HTTPException(status_code=404, detail="Nie znaleziono ćwiczenia")
    return exercise
