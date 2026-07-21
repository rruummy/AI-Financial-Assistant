from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AIQuestion(BaseModel):
    question: str

class AIAnswer(BaseModel):
    answer: str

class ForecastResponse(BaseModel):
    predicted_amount: float
    period: str
    explanation: str