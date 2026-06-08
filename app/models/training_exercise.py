from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import relationship


class TrainingExercise(Base):
    __tablename__ = "training_exercises"

    id = Column(Integer, primary_key=True, index=True)

    training_id = Column(Integer, ForeignKey("trainings.id"), nullable=False)

    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=True)
    supersets_group = Column(String(50), nullable=True)
    exercise_order = Column(Integer, nullable=False)

    training = relationship("Training", back_populates="exercises")

    sets = relationship(
        "ExerciseSet",
        back_populates="exercise",
        cascade="all, delete-orphan"
    )