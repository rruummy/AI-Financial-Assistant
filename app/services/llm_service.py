from app.models.ai_chat import AIChat
from app.models.category import Category
from app.models.transaction import Transaction


class LLMService:

    def ask(self, question: str, history: list[AIChat],) -> str:
        raise NotImplementedError

    def categorize(self, description: str, amount: float, categories: list[Category],) -> dict:
        raise NotImplementedError

    def forecast(self, transactions: list[Transaction],) -> dict:
        raise NotImplementedError