from enum import Enum
from sqlalchemy import ForeignKey, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import (Mapped, mapped_column, relationship)
from app.core.db import Base

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