from pydantic import BaseModel
from typing import Optional


class ExerciseSetBase(BaseModel):
    set_number: int
    weight: str
    reps: str
    tempo: Optional[str] = None
    rest_seconds: Optional[int] = None
    
class ExerciseSetOut(ExerciseSetBase):
    id: int
    training_exercise_id: int

    class Config:
        from_attributes = True
