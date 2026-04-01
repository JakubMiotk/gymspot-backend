from sqlalchemy.orm import Session
from app.models.training import Training
from app.models.training_exercise import TrainingExercise
from app.models.exercise_set import ExerciseSet
from app.schemas.training import TrainingCreate

def _add_exercises_to_training(db: Session, training_id: int, training_data: TrainingCreate):
    for exercise_data in training_data.exercises:
        exercise = TrainingExercise(
            training_id=training_id,
            exercise_name=exercise_data.exercise_name,
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

def get_training(db: Session, training_id: int):
    return db.query(Training).filter(Training.id == training_id).first()

def get_trainings_for_client(db: Session, client_id: int):
    return db.query(Training).filter(Training.client_id == client_id).all()

def get_trainings_for_trainer(db: Session, trainer_id: int):
    return db.query(Training).filter(Training.trainer_id == trainer_id).all()

def get_trainings_by_status(db: Session, status: str):
    return db.query(Training).filter(Training.status == status).all()


def update_training_status(
    db: Session,
    training_id: int,
    status: str | None = None,
    is_paid: bool | None = None
):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        return None

    if status is not None:
        training.status = status

    if is_paid is not None:
        training.is_paid = is_paid

    db.commit()
    db.refresh(training)
    return training

def delete_training(db: Session, training_id: int):
    training = db.query(Training).filter(Training.id == training_id).first()
    if training:
        db.delete(training)
        db.commit()
        return True
    return False

def update_training_date(db: Session, training_id: int, training_date):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        return None

    training.training_date = training_date
    db.commit()
    db.refresh(training)
    return training

