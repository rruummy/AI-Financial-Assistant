from decimal import Decimal
from enum import Enum
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, Numeric, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session,
                            mapped_column, relationship)
from app.core.db_base import Base

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