from sqlalchemy import Column, DateTime, Integer, ForeignKey, String
from app.db.base import Base


class Debt(Base):
    __tablename__ = "debts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    value= Column(Integer, nullable=False)

