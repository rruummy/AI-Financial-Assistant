from app.models.ai_chat import AIChat
from app.models.category import Category
from app.models.transaction import Transaction


def build_chat_messages(question: str, history: list[AIChat],) -> list[dict]:

    messages = [
        {
            "role": "system",
            "content": (
                "You are a financial assistant. "
                "Answer clearly and briefly. "
                "Help users analyze their income, expenses and savings."
            ),
        }
    ]

    for chat in reversed(history):
        messages.append(
            {
                "role": "user",
                "content": chat.question,
            }
        )

        messages.append(
            {
                "role": "assistant",
                "content": chat.answer,
            }
        )

    messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    return messages


def build_category_prompt(
    description: str,
    amount: float,
    categories: list[Category],) -> str:

    prompt = f"""
You are a financial assistant.

Choose ONE category.

Transaction:

Description:
{description}

Amount:
{amount}

Available categories:

"""

    for category in categories:
        prompt += (
            f"- id={category.id}, "
            f"name={category.name}, "
            f"type={category.type.value}\n"
        )

    prompt += """

Return ONLY valid JSON.

Example:

{
    "category_id": 2,
    "category_name": "Food",
    "confidence": 0.97
}

Do not write explanations.
"""

    return prompt


def build_forecast_prompt(
    transactions: list[Transaction],
) -> str:

    prompt = """
You are a financial analyst.

Predict next month's expenses.

Transactions:

"""

    for transaction in transactions:

        prompt += (
            f"Date: {transaction.date}\n"
            f"Amount: {transaction.amount}\n"
            f"Description: {transaction.description}\n"
            f"Category ID: {transaction.category_id}\n\n"
        )

    prompt += """

Return ONLY JSON.

Example:

{
    "predicted_amount": 15230.55,
    "period": "Next month",
    "explanation": "Expenses usually increase because..."
}

Do not write explanations outside JSON.
"""

    return prompt