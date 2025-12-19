from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String, nullable = False)
    city = Column(String, nullable = False)
    country = Column(String, nullable = False)
    cuisine = Column(String, nullable = False)
    price = Column(Integer, nullable = False) 
    avg_rating = Column(Float, nullable = False) 
    total_ratings = Column(Integer, nullable = False)
