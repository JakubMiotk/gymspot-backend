from typing import List, Optional
from pydantic import BaseModel
from app.schemas.exercise_sets import ExerciseSetBase, ExerciseSetOut


class ExerciseBase(BaseModel):
    exercise_name: str
    documented_exercise_id: Optional[int] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseOut(ExerciseBase):
    id: int

    class Config:
        from_attributes = True
    exercise_name: Optional[str] = None
    documented_exercise_id: Optional[int] = None

    class Config:
        from_attributes = True
