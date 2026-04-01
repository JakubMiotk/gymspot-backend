from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base
from sqlalchemy.orm import relationship


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id = Column(Integer, primary_key=True, index=True)

    training_exercise_id = Column(
        Integer,
        ForeignKey("training_exercises.id"),
        nullable=False
    )

    set_number = Column(Integer, nullable=False)
    weight = Column(String(50), nullable=True)
    reps = Column(String(50), nullable=True)
    tempo = Column(String(50), nullable=True)
    rest_seconds = Column(Integer, nullable=True)

    exercise = relationship("TrainingExercise", back_populates="sets")