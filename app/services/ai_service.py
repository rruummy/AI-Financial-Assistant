from app.repositories.ai_chat_repository import AIChatRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.llm_service import LLMService
from app.schemas.ai import AIAnswer, CategorizeRequest, CategorizeResponse, ForecastResponse

class AIService:
    def __init__(self, ai_repository: AIChatRepository,
                 transaction_repository: TransactionRepository,
                 category_repository: CategoryRepository,
                 llm_service: LLMService):
        self.ai_repository = ai_repository
        self.transaction_repository = transaction_repository
        self.category_repository = category_repository
        self.llm_service = llm_service
        
    def ask_question(self, user_id: int, question: str) -> AIAnswer:
        history = self.ai_repository.get_last_messages(user_id=user_id, limit=5)

        answer = self.llm_service.ask(question=question, history=history)

        self.ai_repository.create(user_id=user_id, question=question, answer=answer)
        return AIAnswer(answer=answer)

    def categorize_transaction(self, user_id: int, request: CategorizeRequest) -> CategorizeRequest:
        categories = self.category_repository.get_by_user(user_id)

        result = self.llm_service.categorize(description=request.description,
                                             amount=request.amount,
                                             categories=categories)
        return CategorizeRequest(**request)

    def forecast_expenses(self, user_id: int) -> ForecastResponse:
        transactions = self.transaction_repository.get_by_user(user_id)

        result = self.llm_service.forecast(transactions)

        return ForecastResponse(**result)

    def get_chat_history(self, user_id: int):
        return self.ai_repository.get_history(user_id)

    def get_last_messages(self, user_id: int, limit: int = 5):
        return self.ai_repository.get_last_messages(user_id, limit=limit)

    def clear_history(self, user_id: int) -> None:
        return self.ai_repository.clear_history(user_id)