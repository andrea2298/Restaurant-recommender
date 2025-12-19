##Creación de la tabla (en caso de no existir) y cargar datos de prueba
import os
import pandas as pd
from sqlalchemy import inspect
from sqlalchemy.orm import Session
from models import Base, Restaurant
from db import engine

SEED_PATH = os.path.join(os.path.dirname(__file__), "data", "restaurants_seed.csv")

def init_db():
    inspector = inspect(engine)

    if "restaurants" not in inspector.get_table_names():
        Base.metadata.create_all(engine)

        df = pd.read_csv(SEED_PATH)
        with Session(engine) as session:
            objs = [
                Restaurant(
                    name = row["name"],
                    city = row["city"],
                    country = row["country"],
                    cuisine = row["cuisine"],
                    price = int(row["price"]),
                    avg_rating = float(row["avg_rating"]),
                    total_ratings = int(row["total_ratings"]),
                )

                for _, row in df.iterrows()
            ]

            session.add_all(objs)
            session.commit()
