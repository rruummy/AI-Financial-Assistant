from app.repositories.ai_chat_repository import AIChatRepository
from app.services.ai_tools import TOOLS, ToolExecutor
from app.services.category_service import CategoryService
from app.services.llm_service import LLMService
from app.services.transaction_service import TransactionService
from app.schemas.ai import AIAnswer, ForecastResponse


class AIService:
    def __init__(
        self,
        ai_repository: AIChatRepository,
        transaction_service: TransactionService,
        category_service: CategoryService,
        llm_service: LLMService,
    ):
        self.ai_repository = ai_repository
        self.transaction_service = transaction_service
        self.category_service = category_service
        self.llm_service = llm_service

    def chat(self, user_id: int, question: str) -> AIAnswer:
        history = self.ai_repository.get_last_messages(user_id=user_id, limit=5)

        tool_executor = ToolExecutor(
            user_id=user_id,
            transaction_service=self.transaction_service,
            category_service=self.category_service,
        )

        answer = self.llm_service.ask(
            question=question,
            history=history,
            tool_executor=tool_executor,
            tools=TOOLS,
        )

        self.ai_repository.create(user_id=user_id, question=question, answer=answer)
        return AIAnswer(answer=answer)

    def forecast_expenses(self, user_id: int) -> ForecastResponse:
        transactions = self.transaction_service.get_user_transactions(user_id)

        result = self.llm_service.forecast(transactions)

        return ForecastResponse(**result)

    def get_history(self, user_id: int):
        return self.ai_repository.get_history(user_id)

    def get_last_messages(self, user_id: int, limit: int = 5):
        return self.ai_repository.get_last_messages(user_id, limit=limit)

    def clear_history(self, user_id: int) -> None:
        return self.ai_repository.clear_history(user_id)
