from sqlalchemy import Column, DateTime, Integer, ForeignKey, String
from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    value= Column(Integer, nullable=False)
    type = Column(String(50), nullable=False, default="payment")

