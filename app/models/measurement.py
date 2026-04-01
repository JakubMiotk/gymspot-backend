from sqlalchemy import Column, DateTime, Integer, ForeignKey, SmallInteger, String
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from app.db.base import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)

    weight = Column(DECIMAL(4, 1 ), nullable=False)
    height = Column(SmallInteger, nullable=False)
    body_fat = Column(DECIMAL(3, 1), nullable=True)
    visceral_fat = Column(TINYINT(unsigned=True), nullable=True)
    fat_mass = Column(DECIMAL(4, 1), nullable=True)
    muscle_mass = Column(DECIMAL(4, 1), nullable=True)
    note = Column(String(255), nullable=True)

    segmental_fat = relationship(
        "MeasurementsSegmentalFat",
        back_populates="measurement",
        uselist=False,
        cascade="all, delete-orphan"
    )

    segmental_fat_free = relationship(
        "MeasurementsSegmentalFatFree",
        back_populates="measurement",
        uselist=False,
        cascade="all, delete-orphan"
    )

