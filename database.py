from config import data
from contextlib import contextmanager
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import create_engine, text
from models import User, Role, Importance, Status, Task

DATABASE_SERVER_URL = f"mysql+pymysql://{data['user']}:{data['password']}@{data['host']}:{data['port']}"
DATABASE_URL = f"mysql+pymysql://{data['user']}:{data['password']}@{data['host']}:{data['port']}/{data['database']}"

engine_without_db = create_engine(DATABASE_SERVER_URL, echo=True, future=True)
engine = create_engine(DATABASE_URL, future=True)


def create_database_if_not_exists():
    with engine_without_db.connect() as connection:
        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {data['database']}"))


def create_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    """Создание сессии для FastAPI"""
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()


if __name__ == "__main__":
    create_database_if_not_exists()
    create_tables()
