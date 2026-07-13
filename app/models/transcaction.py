from decimal import Decimal
from enum import Enum
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, Numeric, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import (DeclarativeBase, Mapped, Session,
                            mapped_column, relationship)

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