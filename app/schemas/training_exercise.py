from typing import List, Optional
from pydantic import BaseModel
from app.schemas.exercise_sets import ExerciseSetBase, ExerciseSetOut


class TrainingExerciseBase(BaseModel):
    exercise_id: int
    supersets_group: Optional[int] = None
    exercise_order: int

class TrainingExerciseCreate(TrainingExerciseBase):
    sets: List[ExerciseSetBase]

class TrainingExerciseOut(TrainingExerciseBase):
    id: int
    training_id: int
    sets: List[ExerciseSetOut] = []
    exercise_name: Optional[str] = None
    documented_exercise_id: Optional[int] = None

    class Config:
        from_attributes = True
