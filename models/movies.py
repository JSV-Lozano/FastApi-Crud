from config.database import Base
from sqlalchemy import Column, Integer, String, Float


class Movies(Base):
    __tablename__ = "Movies"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=True)
    overview = Column(String(500), nullable=True)
    year = Column(Integer, nullable=True)
    rating = Column(Float)
    category = Column(String(50), nullable=True)
