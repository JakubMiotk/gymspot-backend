from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.mysql import DECIMAL
from sqlalchemy.orm import relationship

from app.db.base import Base

class BaseSegmentalFat(Base):
    __abstract__ = True  # nie tworzy tabeli w bazie

    id = Column(Integer, primary_key=True, index=True)
    measurement_id = Column(Integer, ForeignKey("measurements.id"), nullable=False)
    left_arm = Column(DECIMAL(4, 1, unsigned=True), nullable=False)
    right_arm = Column(DECIMAL(4, 1, unsigned=True), nullable=False)
    trunk = Column(DECIMAL(4, 1, unsigned=True), nullable=False,)
    left_leg = Column(DECIMAL(4, 1, unsigned=True), nullable=False)
    right_leg = Column(DECIMAL(4, 1, unsigned=True), nullable=False )

class MeasurementsSegmentalFat(BaseSegmentalFat):
    __tablename__ = "measurements_segmental_fat"
    measurement = relationship("Measurement", back_populates="segmental_fat")

class MeasurementsSegmentalFatFree(BaseSegmentalFat):
    __tablename__ = "measurements_segmental_fat_free"
    measurement = relationship("Measurement", back_populates="segmental_fat_free")
