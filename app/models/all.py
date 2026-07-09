from typing import List, Optional
from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import (DeclarativeBase, Mapped,
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
    
    password_hash: Mapped[str] = mapped_column(String(255),
                                               nullable=False)
    
    name: Mapped[str] = mapped_column(String(50),
                                      nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

