import json
import logging

from ollama import Client

from app.core.config import settings
from app.models.ai_chat import AIChat
from app.models.transaction import Transaction
from app.services.ai_tools import ToolExecutor, serialize_tool_result
from app.services.promts import (
    build_chat_messages,
    build_forecast_prompt,
)

logger = logging.getLogger(__name__)

MAX_TOOL_ITERATIONS = 5


class LLMService:

    def __init__(self):
        self.model = "qwen3:8b"
        self.client = Client(host=settings.OLLAMA_URL)

    def _parse_json(self, text: str) -> dict:
        text = text.strip()

        if text.startswith("```json"):
            text = text.removeprefix("```json")

        if text.endswith("```"):
            text = text.removesuffix("```")

        return json.loads(text.strip())

    @staticmethod
    def _tool_call_to_message(tool_calls) -> list[dict]:
        result = []

        for call in tool_calls:
            result.append(
                {
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    }
                }
            )

        return result

    def ask(
        self,
        question: str,
        history: list[AIChat],
        tool_executor: ToolExecutor | None = None,
        tools: list[dict] | None = None,
    ) -> str:

        messages = build_chat_messages(
            question=question,
            history=history,
        )

        try:

            # Звичайний чат без tool calling
            if tool_executor is None or not tools:
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                )

                return response.message.content or ""

            # Tool Calling
            for _ in range(MAX_TOOL_ITERATIONS):

                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                )

                message = response.message

                if not message.tool_calls:
                    return message.content or ""

                messages.append(
                    {
                        "role": "assistant",
                        "content": message.content or "",
                        "tool_calls": self._tool_call_to_message(
                            message.tool_calls
                        ),
                    }
                )

                for call in message.tool_calls:

                    name = call.function.name
                    arguments = dict(call.function.arguments or {})

                    logger.info(
                        "AI tool call: %s(%s)",
                        name,
                        arguments,
                    )

                    result = tool_executor.execute(
                        name=name,
                        arguments=arguments,
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "name": name,
                            "content": serialize_tool_result(result),
                        }
                    )

            # Якщо модель зациклилась
            response = self.client.chat(
                model=self.model,
                messages=messages,
            )

            return (
                response.message.content
                or "Не вдалося завершити запит."
            )

        except Exception as e:
            logger.exception("Ollama error")
            raise RuntimeError(
                f"Failed to connect to Ollama: {e}"
            )

    def forecast(
        self,
        transactions: list[Transaction],
    ) -> dict:

        prompt = build_forecast_prompt(
            transactions=transactions,
        )

        try:

            response = self.client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            return self._parse_json(
                response.message.content
            )

        except Exception as e:
            logger.exception("Forecast error")
            raise RuntimeError(
                f"Forecast failed: {e}"
            )