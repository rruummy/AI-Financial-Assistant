from decimal import Decimal
from enum import Enum
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, Numeric, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session,
                            mapped_column, relationship)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255),
                                       unique=True,
                                       index=True,
                                       nullable=False) 
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user", cascade="all, delete-orphan",)
    categories: Mapped[list["Category"]] = relationship(back_populates="user", cascade="all, delete-orphan",)
    ai_chats: Mapped[list["AIChat"]] = relationship(back_populates="user", cascade="all, delete-orphan",)

class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Category(Base):
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[CategoryType] = mapped_column(SQLEnum(CategoryType), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    
    user: Mapped["User"] = relationship(back_populates="categories",)
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category", cascade="all, delete-orphan",)

class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(100))
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),)
    user: Mapped["User"] = relationship(back_populates="transactions",)
    category: Mapped["Category"] = relationship(back_populates="transactions",)

class AIChat(Base):
    __tablename__ = 'ai_chat'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),)
    user: Mapped["User"] = relationship(back_populates="ai_chats",)

from sqlalchemy import create_engine, select

DATABASE_URL = "postgresql+psycopg://postgres:admin@localhost:5432/expense_tracker"
engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)

with Session(engine) as s:
    s.add(User(email="example1@gmail.com", password_hash="aasd$%sad*12SA6865123SAD%^&*9DF6dsfA=5A5=A++++0",
               name="User1"))
    s.add(User(email="example2@gmail.com", password_hash="aasd$%sad*asdg4ersfasz23SAD%^&*9DF6dsfA=5A5=A++++0",
               name="User2"))
    s.commit()

with Session(engine) as s:
    get_user = select(User).where(User.name == "User2")
    user = s.scalars(get_user).one()
    print(user)

