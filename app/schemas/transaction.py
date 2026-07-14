from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime

class TransactionCreate(BaseModel):
    amount: Decimal
    description: str | None = Field(max_length=100)
    category_id: int

class TransactionUpdate(BaseModel):
    amount: Decimal | None = None
    description: str | None = Field(max_length=100)
    category_id: int | None = None 

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    description: str | None = Field(max_length=100)
    date: datetime
    category_id: int
    user_id: int
    created_at: datetime