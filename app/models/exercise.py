from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import relationship


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String(255), nullable=False)
    documented_exercise_id = Column(Integer, ForeignKey("documentation.id"), nullable=True)