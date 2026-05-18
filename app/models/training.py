from sqlalchemy import Column, DateTime, Enum, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

TRAINING_STATUSES = (
    "planned",
    "started",
    "canceled",
    "missed",
    "completed_paid",
    "completed_unpaid",
)


class Training(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)

    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    training_date = Column(DateTime, nullable=False)

    status = Column(Enum(*TRAINING_STATUSES, name="training_status"), default="planned", nullable=False)
    note = Column(String(255), nullable=True)

    exercises = relationship(
        "TrainingExercise",
        back_populates="training",
        cascade="all, delete-orphan"
    )
