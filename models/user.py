from config.database import Base
from sqlalchemy import Column, String, Integer


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=True, unique=True)
    password = Column(String(100), nullable=True)
    name = Column(String(100), nullable=True)
