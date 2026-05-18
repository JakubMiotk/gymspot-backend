from pydantic import BaseModel

from typing import Optional

class DocumentationBase(BaseModel):
    exercise_name: str
    exercise_description: Optional[str] = None
    exercise_video: Optional[str] = None
    exercise_type : Optional[str] = None
    exercise_body_parts : Optional[str] = None
    author: int

class DocumentationCreate(DocumentationBase):
    pass

class DocumentationOut(DocumentationBase):
    id: int

    class Config:
        from_attributes = True