from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from app.schemas.training_exercise import TrainingExerciseCreate, TrainingExerciseOut


class TrainingBase(BaseModel):
    trainer_id: int
    client_id: int
    training_date: datetime
    note: Optional[str] = None

class TrainingCreate(TrainingBase):
    exercises: List[TrainingExerciseCreate]

class TrainingOut(TrainingBase):
    id: int
    created_at: datetime
    status: str
    is_paid: bool
    exercises: List[TrainingExerciseOut] = []

    class Config:
        from_attributes = True
    
class TrainingStatusUpdate(BaseModel):
    status: Optional[str] = None
    is_paid: Optional[bool] = None

class TrainingDateUpdate(BaseModel):
    training_date: str
