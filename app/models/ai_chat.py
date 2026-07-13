from decimal import Decimal
from enum import Enum
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime, Numeric, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import (Mapped, mapped_column, relationship)
from app.core.db import Base

class AIChat(Base):
    __tablename__ = 'ai_chat'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),)
    user: Mapped["User"] = relationship(back_populates="ai_chats",)
