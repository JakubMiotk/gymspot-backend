import os
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.exercise import Exercise
from app.core.security import get_password_hash, verify_password
from app.schemas.exercise import ExerciseBase

def new_exercise(db: Session, exercise_data: ExerciseBase):
    exercise = Exercise(
        exercise_name=exercise_data.exercise_name,
        documented_exercise_id=exercise_data.documented_exercise_id
    )   
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise

def get_exercise_by_id(db: Session, exercise_id: int):
    return db.query(Exercise).filter(Exercise.id == exercise_id).first()

def get_exercises(db: Session):
    return db.query(Exercise).all()

def update_exercise(db: Session, exercise_id: int, update_data: ExerciseBase):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        return None
    exercise.exercise_name = update_data.exercise_name
    exercise.documented_exercise_id = update_data.documented_exercise_id

    db.commit()
    db.refresh(exercise)
    return exercise


def delete_exercise(db: Session, exercise_id: int):
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if exercise:
        db.delete(exercise)
        db.commit()
        return True
    return False

def get_exercise_name(db: Session, exercise_name: str):
    return db.query(Exercise).filter(
    func.lower(Exercise.exercise_name) == exercise_name.strip().lower()
).first()
    