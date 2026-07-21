import json

from ollama import chat

from app.models.ai_chat import AIChat
from app.models.category import Category
from app.models.transaction import Transaction

from app.services.promts import build_category_prompt, build_chat_messages, build_forecast_prompt


class LLMService:

    def __init__(self):
        self.model = "qwen3:8b"

    def _parse_json(self, text: str) -> dict:
        text = text.strip()

        if text.startswith("```json"):
            text = text.removeprefix("```json")

        if text.endswith("```"):
            text = text.removesuffix("```")

        return json.loads(text.strip())

    def ask(self, question: str, history: list[AIChat]) -> str:
        messages = build_chat_messages(question=question, history=history)
        response = chat(model=self.model, messages=messages,)

        return response.message.content

    def categorize(self, description: str,
                   amount: float,
                   categories: list[Category],) -> dict:
        promt = build_category_prompt(description=description,
                                      amount=amount,
                                      categories=categories)
        responce = chat(model=self.model,
                        messages=[
                            {
                                "role": 'user',
                                "content": promt,
                            }
                        ],
                    )
        return self._parse_json(responce.message.content)

    def forecast(self, transaction: list[Transaction],) -> dict:
        promt = build_forecast_prompt(transactions=transaction)

        responce = chat(model=self.model,
                        messages=[
                            {
                                "role": 'user',
                                "content": promt,
                            }
                        ]
                    )
        return self._parse_json(responce.message.content)