from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AIQuestion(BaseModel):
    question: str

class AIAnswer(BaseModel):
    answer: str

class CategorizeRequest(BaseModel):
    description: str
    amount: float

class CategorizeResponse(BaseModel):
    category_id: int
    category_name: str
    confidence: float

class ForecastResponse(BaseModel):
    predicted_amount: float
    period: str
    explanation: str