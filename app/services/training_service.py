from sqlalchemy.orm import Session, selectinload
from datetime import datetime, timedelta
from app.models.training import Training
from app.models.training_exercise import TrainingExercise
from app.models.exercise_set import ExerciseSet
from app.models.payment import Payment
from app.models.excess_payments import ExcessPayment
from app.models.debts import Debt
from app.schemas.training import TrainingCreate
from app.services.excess_payment_service import consume_excess_payment, consume_all_excess
from app.services.debt_service import upsert_increment_debt, consume_debt, consume_all_debt, get_current_debt_value

TRAINING_PRICES = {
    "personal": 80,
    "group": 40,
}

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
    return (
        db.query(Training)
        .options(
            selectinload(Training.exercises).selectinload(TrainingExercise.sets)
        )
        .filter(Training.id == training_id)
        .first()
    )

def _get_week_window(week_offset: int) -> tuple[datetime, datetime]:
    safe_week_offset = max(week_offset, 0)
    window_end = datetime.utcnow() - timedelta(days=7 * safe_week_offset)
    window_start = window_end - timedelta(days=7)
    return window_start, window_end


def get_trainings_for_client(db: Session, client_id: int, week_offset: int = 0):
    window_start, window_end = _get_week_window(week_offset)
    return (
        db.query(Training)
        .options(
            selectinload(Training.exercises).selectinload(TrainingExercise.sets)
        )
        .filter(Training.client_id == client_id)
        .filter(Training.training_date >= window_start)
        .filter(Training.training_date < window_end)
        .order_by(Training.training_date.desc())
        .all()
    )

def get_trainings_for_trainer(db: Session, trainer_id: int, week_offset: int = 0):
    window_start, window_end = _get_week_window(week_offset)
    return (
        db.query(Training)
        .options(
            selectinload(Training.exercises).selectinload(TrainingExercise.sets)
        )
        .filter(Training.trainer_id == trainer_id)
        .filter(Training.training_date >= window_start)
        .filter(Training.training_date < window_end)
        .order_by(Training.training_date.desc())
        .all()
    )

def get_trainings_by_status(db: Session, status: str):
    return (
        db.query(Training)
        .options(
            selectinload(Training.exercises).selectinload(TrainingExercise.sets)
        )
        .filter(Training.status == status)
        .order_by(Training.training_date.desc())
        .all()
    )


def get_available_excess_for_training(db: Session, training_id: int):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        return None

    available_excess = db.query(ExcessPayment).filter(
        ExcessPayment.user_id == training.client_id
    ).all()

    return sum(payment.value for payment in available_excess)


def update_training_status(
    db: Session,
    training_id: int,
    status: str | None = None,
    payment_training_type: str | None = None,
    use_excess_payment: bool = False,
    use_debt_settlement: bool = False,
):
    training = db.query(Training).filter(Training.id == training_id).first()
    if not training:
        return None

    should_charge_training = status == "completed_paid" and training.status != "completed_paid"
    should_debt_training = status == "completed_unpaid" and training.status != "completed_unpaid"

    if should_charge_training:
        if payment_training_type not in TRAINING_PRICES:
            raise ValueError("Wybierz typ treningu do rozliczenia")

        training_price = TRAINING_PRICES[payment_training_type]

        if use_excess_payment:
            if consume_excess_payment(db, training.client_id, training_price):
                pass  # full excess used, no remainder
            else:
                consumed = consume_all_excess(db, training.client_id)
                remainder = training_price - consumed
                if remainder > 0:
                    upsert_increment_debt(db, training.client_id, remainder)
        else:
            if use_debt_settlement:
                current_debt = get_current_debt_value(db, training.client_id)
                if current_debt >= training_price:
                    consume_debt(db, training.client_id, training_price)
                    payment = Payment(
                        from_user_id=training.client_id,
                        to_user_id=training.trainer_id,
                        date=datetime.utcnow(),
                        value=training_price,
                        type="regulacja",
                    )
                    db.add(payment)
                elif current_debt > 0:
                    consume_all_debt(db, training.client_id)
                    payment_regulacja = Payment(
                        from_user_id=training.client_id,
                        to_user_id=training.trainer_id,
                        date=datetime.utcnow(),
                        value=current_debt,
                        type="regulacja",
                    )
                    db.add(payment_regulacja)
                    payment_rest = Payment(
                        from_user_id=training.client_id,
                        to_user_id=training.trainer_id,
                        date=datetime.utcnow(),
                        value=training_price - current_debt,
                        type="payment",
                    )
                    db.add(payment_rest)
                else:
                    payment = Payment(
                        from_user_id=training.client_id,
                        to_user_id=training.trainer_id,
                        date=datetime.utcnow(),
                        value=training_price,
                        type="payment",
                    )
                    db.add(payment)
            else:
                payment = Payment(
                    from_user_id=training.client_id,
                    to_user_id=training.trainer_id,
                    date=datetime.utcnow(),
                    value=training_price,
                    type="payment",
                )
                db.add(payment)

    if should_debt_training:
        if payment_training_type not in TRAINING_PRICES:
            raise ValueError("Wybierz typ treningu do rozliczenia")

        training_price = TRAINING_PRICES[payment_training_type]
        upsert_increment_debt(db, training.client_id, training_price)

    if status is not None:
        training.status = status

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

