"""
Опис "інструментів" (function calling) для ШІ-агента та їх виконання.

Ідея: LLM не працює з БД напряму. Замість цього моделі надається список
доступних функцій (TOOLS) з JSON Schema параметрів. Коли модель вирішує,
що потрібно щось зробити з даними користувача (додати транзакцію,
створити категорію, порахувати баланс і т.д.), вона повертає tool_call
з назвою функції та аргументами. AIService.chat перехоплює цей виклик,
виконує відповідний метод у ToolExecutor (який працює через уже наявні
TransactionService / CategoryService - з усією їх валідацією), і повертає
результат назад моделі, щоб вона сформулювала фінальну відповідь людині.

Це тримає бізнес-логіку (перевірку прав, дублікатів і т.п.) в одному
місці - у сервісах, а не дублює її в LLM-шарі.
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from app.models.category import CategoryType
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.services.category_service import CategoryService
from app.services.transaction_service import TransactionService


# ---------------------------------------------------------------------------
# Схеми інструментів у форматі, який очікує ollama / OpenAI-style tool calling
# ---------------------------------------------------------------------------

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_categories",
            "description": (
                "Повертає список усіх категорій (доходи/витрати) поточного "
                "користувача разом з їх id. Використовуй перед створенням "
                "транзакції, якщо не впевнений, чи існує потрібна категорія."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_category",
            "description": "Створює нову категорію доходів або витрат для користувача.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Назва категорії, наприклад 'Продукти' або 'Зарплата'.",
                    },
                    "category_type": {
                        "type": "string",
                        "enum": ["income", "expense"],
                        "description": "Тип категорії: income (дохід) або expense (витрата).",
                    },
                },
                "required": ["name", "category_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_category",
            "description": "Перейменовує категорію або змінює її тип (income/expense).",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_name": {
                        "type": "string",
                        "description": "Поточна назва категорії, яку потрібно змінити.",
                    },
                    "new_name": {
                        "type": "string",
                        "description": "Нова назва категорії (опційно).",
                    },
                    "new_type": {
                        "type": "string",
                        "enum": ["income", "expense"],
                        "description": "Новий тип категорії (опційно).",
                    },
                },
                "required": ["category_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_category",
            "description": "Видаляє категорію користувача разом з усіма її транзакціями.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_name": {
                        "type": "string",
                        "description": "Назва категорії, яку потрібно видалити.",
                    },
                },
                "required": ["category_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_transaction",
            "description": (
                "Додає нову транзакцію (дохід або витрату) користувачу. "
                "Категорія має вже існувати - якщо не впевнений, спочатку "
                "виклич list_categories, а за потреби створи категорію через create_category."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Сума транзакції, додатне число.",
                    },
                    "category_name": {
                        "type": "string",
                        "description": "Назва існуючої категорії користувача.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Короткий опис транзакції (опційно).",
                    },
                },
                "required": ["amount", "category_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_transaction",
            "description": "Оновлює суму, опис або категорію існуючої транзакції за її id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {"type": "integer"},
                    "amount": {"type": "number"},
                    "description": {"type": "string"},
                    "category_name": {"type": "string"},
                },
                "required": ["transaction_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_transaction",
            "description": "Видаляє транзакцію за її id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transaction_id": {"type": "integer"},
                },
                "required": ["transaction_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_transactions",
            "description": (
                "Повертає список транзакцій користувача. Можна відфільтрувати "
                "за назвою категорії та/або періодом (дати у форматі YYYY-MM-DD)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category_name": {"type": "string"},
                    "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "limit": {
                        "type": "integer",
                        "description": "Максимальна кількість транзакцій у відповіді (за замовчуванням 20).",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_statistics",
            "description": "Повертає сумарний дохід, витрати та баланс користувача за весь час.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
]


class ToolExecutor:
    """Виконує tool call-и моделі, викликаючи реальні сервіси в межах одного user_id."""

    def __init__(
        self,
        user_id: int,
        transaction_service: TransactionService,
        category_service: CategoryService,
    ):
        self.user_id = user_id
        self.transaction_service = transaction_service
        self.category_service = category_service

    # -- публічна точка входу -------------------------------------------------

    def execute(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        handler = getattr(self, f"_tool_{name}", None)

        if handler is None:
            return {"error": f"Невідомий інструмент '{name}'."}

        try:
            return handler(**(arguments or {}))
        except TypeError as e:
            return {"error": f"Некоректні аргументи для '{name}': {e}"}
        except ValueError as e:
            return {"error": str(e)}
        except Exception as e:  # noqa: BLE001 - не даємо агенту падати повністю
            return {"error": f"Не вдалося виконати '{name}': {e}"}

    # -- допоміжне ---------------------------------------------------------

    def _find_category(self, category_name: str):
        categories = self.category_service.get_user_category(self.user_id)
        match = next(
            (c for c in categories if c.name.strip().lower() == category_name.strip().lower()),
            None,
        )
        if match is None:
            available = [c.name for c in categories]
            raise ValueError(
                f"Категорію '{category_name}' не знайдено. "
                f"Доступні категорії: {available if available else 'немає жодної, спочатку створи категорію.'}"
            )
        return match

    @staticmethod
    def _parse_amount(amount: Any) -> Decimal:
        try:
            return Decimal(str(amount))
        except (InvalidOperation, ValueError):
            raise ValueError(f"'{amount}' не є коректним числом для суми.")

    @staticmethod
    def _parse_date(value: str) -> datetime:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            raise ValueError(f"Дата '{value}' має бути у форматі YYYY-MM-DD.")

    @staticmethod
    def _transaction_to_dict(transaction) -> dict[str, Any]:
        return {
            "id": transaction.id,
            "amount": str(transaction.amount),
            "description": transaction.description,
            "category_id": transaction.category_id,
            "date": transaction.date.isoformat() if transaction.date else None,
        }

    # -- категорії -----------------------------------------------------------

    def _tool_list_categories(self) -> dict[str, Any]:
        categories = self.category_service.get_user_category(self.user_id)
        return {
            "categories": [
                {"id": c.id, "name": c.name, "type": c.type.value}
                for c in categories
            ]
        }

    def _tool_create_category(self, name: str, category_type: str) -> dict[str, Any]:
        category_data = CategoryCreate(name=name, category_type=CategoryType(category_type))
        category = self.category_service.create_category(category_data, self.user_id)
        return {
            "success": True,
            "category": {"id": category.id, "name": category.name, "type": category.type.value},
        }

    def _tool_update_category(
        self,
        category_name: str,
        new_name: str | None = None,
        new_type: str | None = None,
    ) -> dict[str, Any]:
        category = self._find_category(category_name)

        if category.user_id != self.user_id:
            return {"error": "Ця категорія не належить користувачу."}

        update_data = CategoryUpdate(
            name=new_name,
            category_type=CategoryType(new_type) if new_type else None,
        )
        updated = self.category_service.update_category(category.id, update_data)
        return {
            "success": True,
            "category": {"id": updated.id, "name": updated.name, "type": updated.type.value},
        }

    def _tool_delete_category(self, category_name: str) -> dict[str, Any]:
        category = self._find_category(category_name)

        if category.user_id != self.user_id:
            return {"error": "Ця категорія не належить користувачу."}

        self.category_service.delete_category(category.id)
        return {"success": True, "deleted_category": category_name}

    # -- транзакції ----------------------------------------------------------

    def _tool_create_transaction(
        self,
        amount: Any,
        category_name: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        category = self._find_category(category_name)

        if category.user_id != self.user_id:
            return {"error": "Ця категорія не належить користувачу."}

        transaction_data = TransactionCreate(
            amount=self._parse_amount(amount),
            description=description,
            category_id=category.id,
        )
        transaction = self.transaction_service.create_transaction(transaction_data, self.user_id)
        return {"success": True, "transaction": self._transaction_to_dict(transaction)}

    def _tool_update_transaction(
        self,
        transaction_id: int,
        amount: Any = None,
        description: str | None = None,
        category_name: str | None = None,
    ) -> dict[str, Any]:
        transaction = self.transaction_service.get_transaction(transaction_id)

        if transaction.user_id != self.user_id:
            return {"error": "Ця транзакція не належить користувачу."}

        category_id = None
        if category_name is not None:
            category = self._find_category(category_name)
            if category.user_id != self.user_id:
                return {"error": "Ця категорія не належить користувачу."}
            category_id = category.id

        update_data = TransactionUpdate(
            amount=self._parse_amount(amount) if amount is not None else None,
            description=description,
            category_id=category_id,
        )
        updated = self.transaction_service.update_transaction(transaction_id, update_data)
        return {"success": True, "transaction": self._transaction_to_dict(updated)}

    def _tool_delete_transaction(self, transaction_id: int) -> dict[str, Any]:
        transaction = self.transaction_service.get_transaction(transaction_id)

        if transaction.user_id != self.user_id:
            return {"error": "Ця транзакція не належить користувачу."}

        self.transaction_service.delete_transaction(transaction_id)
        return {"success": True, "deleted_transaction_id": transaction_id}

    def _tool_list_transactions(
        self,
        category_name: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        if category_name is not None:
            category = self._find_category(category_name)
            if category.user_id != self.user_id:
                return {"error": "Ця категорія не належить користувачу."}
            transactions = self.transaction_service.get_transactions_by_category(
                self.user_id, category.id
            )
        elif start_date is not None and end_date is not None:
            transactions = self.transaction_service.get_transactions_by_period(
                self.user_id, self._parse_date(start_date), self._parse_date(end_date)
            )
        else:
            transactions = self.transaction_service.get_user_transactions(self.user_id)

        transactions = sorted(transactions, key=lambda t: t.date, reverse=True)[: max(1, min(limit, 100))]

        return {"transactions": [self._transaction_to_dict(t) for t in transactions]}

    def _tool_get_statistics(self) -> dict[str, Any]:
        stats = self.transaction_service.get_statistics(self.user_id)
        return {
            "income": str(stats["income"]),
            "expense": str(stats["expense"]),
            "balance": str(stats["balance"]),
        }


def serialize_tool_result(result: dict[str, Any]) -> str:
    """JSON-серіалізація результату інструменту для передачі назад у модель."""
    return json.dumps(result, ensure_ascii=False, default=str)
