from sqlalchemy import Column, Integer, ForeignKey
from app.db.base import Base

class Relation(Base):
    __tablename__ = "relations"

    client_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    trainer_id = Column(Integer, ForeignKey("users.id"), primary_key=True)