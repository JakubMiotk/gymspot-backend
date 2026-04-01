from sqlalchemy import Column, Date, Enum, Integer, Numeric, String, ForeignKey
from app.db.base import Base

class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    gender = Column(Enum("M", "K", name="gender_enum"), nullable=False)

    height = Column(Integer, nullable=False)
    weight = Column(Numeric(5, 2), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    city = Column(String(150), nullable=False)
    avatar = Column(String(255), nullable=True)
