from datetime import datetime
from typing import List, Literal, Optional

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
    exercises: List[TrainingExerciseOut] = []

    class Config:
        from_attributes = True
    
class TrainingStatusUpdate(BaseModel):
    status: Optional[Literal[
        "planned",
        "started",
        "canceled",
        "missed",
        "completed_paid",
        "completed_unpaid",
    ]] = None
    payment_training_type: Optional[Literal["personal", "group"]] = None
    use_excess_payment: bool = False
    use_debt_settlement: bool = False

class TrainingCompletionPreview(BaseModel):
    available_excess: int

class TrainingDateUpdate(BaseModel):
    training_date: str
