from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.measurement import MeasurementCreate, MeasurementOut
from app.services.measurement_service import (
    create_measurement,
    get_measurement,
    get_user_measurements,
    update_measurement,
    delete_measurement
)

router = APIRouter(tags=["measurements"])

# Utworzenie nowego pomiaru
@router.post("/", response_model=MeasurementOut)
def create_new_measurement(
    measurement: MeasurementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    measurement_data = measurement.model_copy(update={"user_id": current_user.id})
    return create_measurement(db, measurement_data)

# Pobranie wszystkich pomiarów dla użytkownika
@router.get("/user/{user_id}", response_model=List[MeasurementOut])
def read_measurements_for_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    return get_user_measurements(db, current_user.id)

# Pobranie pomiaru po id
@router.get("/{measurement_id}", response_model=MeasurementOut)
def read_measurement(
    measurement_id: int,
    db: Session = Depends(get_db)):
    measurement = get_measurement(db, measurement_id)

    if not measurement:
        raise HTTPException(status_code=404, detail="Nie znaleziono pomiaru")

    return measurement

 # Aktualizacja pomiaru w bazie danych
@router.put("/{measurement_id}", response_model=MeasurementOut)
def edit_measurement(
    measurement_id: int,
    measurement_data: MeasurementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)):
    measurement_payload = measurement_data.model_copy(update={"user_id": current_user.id})
    measurement = update_measurement(db, measurement_id, measurement_payload)

    if not measurement:
        raise HTTPException(status_code=404, detail="Nie znaleziono pomiaru")

    return measurement

 # Usunięcie pomiaru
@router.delete("/{measurement_id}")
def remove_measurement(
    measurement_id: int,
    db: Session = Depends(get_db)):
    success = delete_measurement(db, measurement_id)

    if not success:
        raise HTTPException(status_code=404, detail="Nie znaleziono pomiaru")

    return {"msg": "Pomiar został usunięty"}
