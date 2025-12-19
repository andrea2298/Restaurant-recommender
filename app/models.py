##Definición de las tablas a utilizar
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
    price = Column(Integer, nullable = False) ##Se dará un rating de 1 a 4
    avg_rating = Column(Float, nullable = False) ##Se dará un rating de 0 a 5
    total_ratings = Column(Integer, nullable = False)