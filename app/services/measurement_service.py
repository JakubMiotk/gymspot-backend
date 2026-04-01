from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional

from app.models.measurement import Measurement
from app.models.measurement_segmental import MeasurementsSegmentalFat, MeasurementsSegmentalFatFree

from app.schemas.measurement import MeasurementCreate

def create_measurement(
    db: Session,
    data: MeasurementCreate
) -> Measurement:

    measurement = Measurement(
        user_id=data.user_id,
        date=data.date,
        weight=data.weight,
        height=data.height,
        body_fat=data.body_fat,
        visceral_fat=data.visceral_fat,
        fat_mass=data.fat_mass,
        muscle_mass=data.muscle_mass,
        note=data.note
    )

    measurement.segmental_fat = MeasurementsSegmentalFat(
        left_arm=data.segmental_fat.left_arm,
        right_arm=data.segmental_fat.right_arm,
        trunk=data.segmental_fat.trunk,
        left_leg=data.segmental_fat.left_leg,
        right_leg=data.segmental_fat.right_leg,
    )

    measurement.segmental_fat_free = MeasurementsSegmentalFatFree(
        left_arm=data.segmental_fat_free.left_arm,
        right_arm=data.segmental_fat_free.right_arm,
        trunk=data.segmental_fat_free.trunk,
        left_leg=data.segmental_fat_free.left_leg,
        right_leg=data.segmental_fat_free.right_leg,
    )

    db.add(measurement)
    db.commit()
    db.refresh(measurement)

    return measurement


from sqlalchemy.orm import joinedload

def get_measurement(db: Session, measurement_id: int):

    return db.query(Measurement).options(
        joinedload(Measurement.segmental_fat),
        joinedload(Measurement.segmental_fat_free)
    ).filter(
        Measurement.id == measurement_id
    ).first()


def get_user_measurements(
    db: Session,
    user_id: int) -> List[Measurement]:

    return db.query(Measurement).filter(
        Measurement.user_id == user_id).order_by(Measurement.date.desc()).all()

def update_measurement(
    db: Session,
    measurement_id: int,
    data: MeasurementCreate
) -> Optional[Measurement]:

    measurement = db.query(Measurement).filter(
        Measurement.id == measurement_id
    ).first()

    if not measurement:
        return None

    measurement.date = data.date
    measurement.weight = data.weight
    measurement.height = data.height
    measurement.body_fat = data.body_fat
    measurement.visceral_fat = data.visceral_fat
    measurement.fat_mass = data.fat_mass
    measurement.muscle_mass = data.muscle_mass
    measurement.note = data.note

    db.commit()
    db.refresh(measurement)

    return measurement

def delete_measurement(
    db: Session,
    measurement_id: int) -> bool:

    measurement = db.query(Measurement).filter(
        Measurement.id == measurement_id
    ).first()

    if not measurement:
        return False

    db.delete(measurement)
    db.commit()

    return True
