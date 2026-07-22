from pydantic import BaseModel

class AIQuestion(BaseModel):
    question: str

class AIAnswer(BaseModel):
    answer: str

class ForecastResponse(BaseModel):
    predicted_amount: float
    period: str
    explanation: str