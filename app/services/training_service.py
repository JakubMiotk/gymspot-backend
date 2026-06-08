from sqlalchemy.orm import Session, selectinload
from datetime import datetime

from app.models.training import Training
from app.models.training_exercise import TrainingExercise
from app.models.exercise_set import ExerciseSet
from app.models.exercise import Exercise

from app.models.payment import Payment
from app.models.excess_payments import ExcessPayment
from app.models.debts import Debt

from app.schemas.training import TrainingCreate

from app.services.excess_payment_service import (
    consume_excess_payment,
    consume_all_excess
)
from app.services.debt_service import (
    upsert_increment_debt,
    consume_debt,
    consume_all_debt,
    get_current_debt_value
)

TRAINING_PRICES = {
    "personal": 80,
    "group": 40,
}

# =========================
# MAPPING EXERCISES
# =========================

def _map_training_exercises_with_names(db: Session, training: Training):
    exercise_ids = [e.exercise_id for e in training.exercises]

    if not exercise_ids:
        return []

    exercises = (
        db.query(Exercise)
        .filter(Exercise.id.in_(exercise_ids))
        .all()
    )

    exercise_map = {e.id: e.exercise_name for e in exercises}

    result = []
    for ex in training.exercises:
        result.append({
            "id": ex.id,
            "exercise_id": ex.exercise_id,
            "exercise_name": exercise_map.get(ex.exercise_id),
            "supersets_group": ex.supersets_group,
            "exercise_order": ex.exercise_order,
            "sets": [
                {
                    "id": s.id,
                    "set_number": s.set_number,
                    "weight": s.weight,
                    "reps": s.reps,
                    "tempo": s.tempo,
                    "rest_seconds": s.rest_seconds,
                }
                for s in ex.sets
            ]
        })

    return result


def _map_trainings_list(db: Session, trainings):
    return [
        {
            "id": t.id,
            "trainer_id": t.trainer_id,
            "client_id": t.client_id,
            "training_date": t.training_date,
            "note": t.note,
            "status": t.status,
            "exercises": _map_training_exercises_with_names(db, t),
        }
        for t in trainings
    ]


# =========================
# CORE TRAINING LOGIC
# =========================

def _add_exercises_to_training(db: Session, training_id: int, training_data: TrainingCreate):
    for exercise_data in training_data.exercises:
        exercise = TrainingExercise(
            training_id=training_id,
            exercise_id=exercise_data.exercise_id,
            supersets_group=exercise_data.supersets_group,
            exercise_order=exercise_data.exercise_order
        )

        db.add(exercise)
        db.flush()

        for set_data in exercise_data.sets:
            exercise_set = ExerciseSet(
                training_exercise_id=exercise.id,
                set_number=set_data.set_number,
                weight=set_data.weight,
                reps=set_data.reps,
                tempo=set_data.tempo,
                rest_seconds=set_data.rest_seconds
            )
            db.add(exercise_set)


# =========================
# CREATE / UPDATE
# =========================

def create_training(db: Session, training_data: TrainingCreate):
    training = Training(
        trainer_id=training_data.trainer_id,
        client_id=training_data.client_id,
        training_date=training_data.training_date,
        note=training_data.note
    )

    db.add(training)
    db.flush()

    _add_exercises_to_training(db, training.id, training_data)

    db.commit()
    db.refresh(training)
    return training


def update_training(db: Session, training_id: int, training_data: TrainingCreate):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        return None

    training.trainer_id = training_data.trainer_id
    training.client_id = training_data.client_id
    training.training_date = training_data.training_date
    training.note = training_data.note

    training.exercises.clear()
    db.flush()

    _add_exercises_to_training(db, training.id, training_data)

    db.commit()
    db.refresh(training)
    return training


# =========================
# GETTERS (WITH MAPPING)
# =========================

def get_training(db: Session, training_id: int):
    training = (
        db.query(Training)
        .options(
            selectinload(Training.exercises)
            .selectinload(TrainingExercise.sets)
        )
        .filter(Training.id == training_id)
        .first()
    )

    if not training:
        return None

    return {
        "id": training.id,
        "trainer_id": training.trainer_id,
        "client_id": training.client_id,
        "training_date": training.training_date,
        "note": training.note,
        "status": training.status,
        "exercises": _map_training_exercises_with_names(db, training),
    }


def get_trainings_for_client(db: Session, client_id: int, offset: int = 0, limit: int = 30):
    safe_offset = max(offset, 0)
    safe_limit = max(1, min(limit, 100))

    trainings = (
        db.query(Training)
        .options(
            selectinload(Training.exercises)
            .selectinload(TrainingExercise.sets)
        )
        .filter(Training.client_id == client_id)
        .order_by(Training.training_date.desc())
        .offset(safe_offset)
        .limit(safe_limit)
        .all()
    )

    return _map_trainings_list(db, trainings)


def get_trainings_for_trainer(db: Session, trainer_id: int, offset: int = 0, limit: int = 30):
    safe_offset = max(offset, 0)
    safe_limit = max(1, min(limit, 100))

    trainings = (
        db.query(Training)
        .options(
            selectinload(Training.exercises)
            .selectinload(TrainingExercise.sets)
        )
        .filter(Training.trainer_id == trainer_id)
        .order_by(Training.training_date.desc())
        .offset(safe_offset)
        .limit(safe_limit)
        .all()
    )

    return _map_trainings_list(db, trainings)


def get_trainings_by_status(db: Session, status: str):
    trainings = (
        db.query(Training)
        .options(
            selectinload(Training.exercises)
            .selectinload(TrainingExercise.sets)
        )
        .filter(Training.status == status)
        .order_by(Training.training_date.desc())
        .all()
    )

    return _map_trainings_list(db, trainings)


# =========================
# DELETE
# =========================

def delete_training(db: Session, training_id: int):
    training = db.query(Training).filter(Training.id == training_id).first()
    if training:
        db.delete(training)
        db.commit()
        return True
    return False


# =========================
# DATE UPDATE
# =========================

def update_training_date(db: Session, training_id: int, training_date):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        return None

    training.training_date = training_date
    db.commit()
    db.refresh(training)
    return training