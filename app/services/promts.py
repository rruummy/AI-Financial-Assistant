from app.models.ai_chat import AIChat
from app.models.transaction import Transaction


def build_chat_messages(question: str, history: list[AIChat],) -> list[dict]:

    messages = [
        {
            "role": "system",
            "content": (
                "You are a financial assistant with access to the user's real "
                "transactions and categories through tools (function calling). "
                "Answer clearly and briefly, in the same language the user writes in.\n\n"
                "Rules:\n"
                "- Never invent balances, transactions or categories - always call "
                "the relevant tool to get real data before answering questions about "
                "money (balance, statistics, list of transactions/categories).\n"
                "- To add a transaction, first make sure the category exists: call "
                "list_categories, and if it's missing, create it with create_category "
                "before creating the transaction, unless the user already told you the "
                "exact existing category name.\n"
                "- If a tool call returns an error (e.g. category not found), explain "
                "the problem to the user in plain language and suggest a fix instead of "
                "guessing or retrying blindly.\n"
                "- After a tool call succeeds, confirm to the user in plain language "
                "what was actually done (amount, category, etc.), don't just repeat raw JSON.\n"
                "- Ask a short clarifying question only if a required detail (e.g. amount "
                "or category) is truly missing and cannot be reasonably assumed."
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