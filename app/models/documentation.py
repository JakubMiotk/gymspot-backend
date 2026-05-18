from sqlalchemy import Column, Integer, String, ForeignKey, Text
from app.db.base import Base
from sqlalchemy.orm import relationship


class Documentation(Base):
    __tablename__ = "documentation"

    id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(String(255), nullable=False)
    exercise_description = Column(Text, nullable=True)
    exercise_video = Column(String(255), nullable=True)
    exercise_type = Column(String(45), nullable=True)
    exercise_body_parts = Column(String(255), nullable=True)
    author = Column(Integer, ForeignKey("users.id"), nullable=False)
