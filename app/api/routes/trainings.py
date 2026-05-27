from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.training import TrainingCompletionPreview, TrainingCreate, TrainingDateUpdate, TrainingOut, TrainingStatusUpdate
from app.services.training_service import (
    create_training,
    get_available_excess_for_training,
    get_training,
    get_trainings_by_status,
    get_trainings_for_client,
    get_trainings_for_trainer,
    update_training,
    update_training_status,
    delete_training,
    update_training_date
)

router = APIRouter(tags=["trainings"])

@router.post("/", response_model=TrainingOut)
def create_new_training(
    training: TrainingCreate,
    db: Session = Depends(get_db)):
    return create_training(db, training)

@router.get("/{training_id}", response_model=TrainingOut)
def read_training(
    training_id: int,
    db: Session = Depends(get_db)):
    training = get_training(db, training_id)
    if not training:
        raise HTTPException(status_code=404, detail="Nie znaleziono treningu")
    return training

@router.get("/{training_id}/completion-preview", response_model=TrainingCompletionPreview)
def read_training_completion_preview(
    training_id: int,
    db: Session = Depends(get_db)):
    available_excess = get_available_excess_for_training(db, training_id)
    if available_excess is None:
        raise HTTPException(status_code=404, detail="Nie znaleziono treningu")
    return TrainingCompletionPreview(available_excess=available_excess)

@router.put("/{training_id}", response_model=TrainingOut)
def update_existing_training(
    training_id: int,
    training: TrainingCreate,
    db: Session = Depends(get_db)
):
    updated_training = update_training(db, training_id, training)
    if not updated_training:
        raise HTTPException(status_code=404, detail="Nie znaleziono treningu")
    return updated_training

@router.get("/client/{client_id}", response_model=List[TrainingOut])
def read_trainings_for_client(
    client_id: int,
    offset: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db)):
    return get_trainings_for_client(db, client_id, offset=offset, limit=limit)

@router.get("/trainer/{trainer_id}", response_model=List[TrainingOut])
def read_trainings_for_trainer(
    trainer_id: int,
    offset: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db)):
    return get_trainings_for_trainer(db, trainer_id, offset=offset, limit=limit)


@router.patch("/{training_id}/status", response_model=TrainingOut)
def change_training_status(
    training_id: int,
    status: TrainingStatusUpdate,
    db: Session = Depends(get_db)):
    try:
        training = update_training_status(
            db,
            training_id,
            status=status.status,
            payment_training_type=status.payment_training_type,
            use_excess_payment=status.use_excess_payment,
            use_debt_settlement=status.use_debt_settlement,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not training:
        raise HTTPException(status_code=404, detail="Nie znaleziono treningu")

    return training


@router.patch("/{training_id}/date", response_model=TrainingOut)
def change_training_date(
    training_id: int,
    date_update: TrainingDateUpdate,
    db: Session = Depends(get_db)):
    training = update_training_date(
        db,
        training_id,
        training_date=date_update.training_date
    )

    if not training:
        raise HTTPException(status_code=404, detail="Nie znaleziono treningu")

    return training

@router.delete("/{training_id}")
def remove_training(
    training_id: int,
    db: Session = Depends(get_db)):
    success = delete_training(db, training_id)
    if not success:
        raise HTTPException(status_code=404, detail="Nie znaleziono treningu")

    return {"msg": "Trening został usunięty"}

@router.get("/status/{status}", response_model=List[TrainingOut])
def read_trainings_by_status(
    status: str,
    db: Session = Depends(get_db)):
    return get_trainings_by_status(db, status)
