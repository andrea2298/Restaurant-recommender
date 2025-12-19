##Configuración de conexión a PostgreSQL
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "grima")
DB_PASSWORD = os.getenv("DB_PASSWORD", "grima_pass")
DB_NAME = os.getenv("DB_NAME", "grima_rest")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping = True)

SessionLocal = sessionmaker(bind = engine, autoflush = False, autocommit = False)