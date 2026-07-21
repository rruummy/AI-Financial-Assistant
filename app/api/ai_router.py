from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_ai_service, get_current_user
from app.models.user import User
from app.schemas.ai import AIQuestion, AIAnswer, ForecastResponse
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat", response_model=AIAnswer)
def chat(
    question: AIQuestion,
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)):
    try:
        return ai_service.chat(current_user.id, question.question)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/forecast", response_model=ForecastResponse)
def forecast_expenses(
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)):
    try:
        return ai_service.forecast_expenses(current_user.id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/history")
def history(
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)):
    return ai_service.get_history(current_user.id)


@router.get("/history/last")
def last_messages(
    limit: int = 5,
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service),):
    return ai_service.get_last_messages(current_user.id, limit)

@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_history(
    current_user: User = Depends(get_current_user),
    ai_service: AIService = Depends(get_ai_service)):
    ai_service.clear_history(current_user.id)