from sqlalchemy import Column, DateTime, Boolean, Enum, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Training(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)

    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    training_date = Column(DateTime, nullable=False)

    status = Column(Enum("planned", "completed", "canceled", "started", name="training_status"), default="pending", nullable=False)
    is_paid = Column(Boolean, default=False, nullable=False)
    note = Column(String(255), nullable=True)

    exercises = relationship(
        "TrainingExercise",
        back_populates="training",
        cascade="all, delete-orphan"
    )
