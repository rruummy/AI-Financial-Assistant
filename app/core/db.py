from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine, select

DATABASE_URL = "postgresql+psycopg://postgres:admin@localhost:5432/expense_tracker"
engine = create_engine(DATABASE_URL, echo=True)

class Base(DeclarativeBase):
    pass