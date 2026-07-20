from datetime import datetime
from decimal import Decimal
from app.models.transaction import Transaction
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate

class TransactionService:
    def __init__(self, transaction_repository: TransactionRepository,
                 category_repository: CategoryRepository):
        self.transaction_repository = transaction_repository
        self.category_repository = category_repository 

    # CRUD
    def create_transaction(self, transaction_data: TransactionCreate) -> Transaction:
        category = self.category_repository.get_by_id(transaction_data.category_id)

        if category is None:
            raise ValueError("Transaction not found.")

        if category.user_id != transaction_data.user_id:
            raise ValueError("Category does not belong to this user.")

        return self.transaction_repository.create(transaction_data)
    
    def get_transaction(self, transaction_id: int) -> Transaction:
        transaction = self.transaction_repository.get_by_id(transaction_id)

        if transaction is None:
            raise ValueError("Transaction not found.")

        return transaction        

    def get_user_transaction(self, user_id: int) -> list[Transaction]:
        return self.transaction_repository.get_by_user(user_id)

    def update_transaction(self, transaction_id: int, transaction_data: TransactionUpdate):
        transaction = self.transaction_repository.get_by_id(transaction_id)

        if transaction is None:
            raise ValueError("Transaction not found.")

        if transaction_data.category_id is not None:
            category = self.category_repository.get_by_id(transaction_data.category_id)
            if category is None:
                raise ValueError("Category not found.")
            if category.user_id != transaction.user_id:
                raise ValueError("Category does not belong to this user.")

            transaction.category_id = transaction_data.category_id

        if transaction_data.amount is not None:
            transaction.amount = transaction_data.amount

        if transaction_data.description is not None:
            transaction.description = transaction_data.description

        return self.transaction_repository.update(transaction)

    def delete_transaction(self, transaction_id: int) -> None:
        transaction = self.transaction_repository.get_by_id(transaction_id)

        if transaction is None:
            raise ValueError("Transaction not found.")

        self.transaction_repository.delete(transaction)

    # Search
    def get_transaction_by_category(self, user_id: int, category_id: int) -> list[Transaction]:
        return self.transaction_repository.get_by_category(user_id=user_id, category_id=category_id)

    def get_transaction_by_period(self, user_id: int,
                                  start_date: datetime,
                                  end_date: datetime) -> list[Transaction]:
        if start_date > end_date:
            raise ValueError("Start date cannot be later than end date.")

        return self.transaction_repository.get_by_period(user_id, start_date, end_date)

    # Statistic
    def get_total_income(self, user_id: int) -> Decimal:
        return self.transaction_repository.get_total_income(user_id)
        

    def get_total_expense(self, user_id: int) -> Decimal:
        return self.transaction_repository.get_total_expense(user_id)

    def get_balance(self, user_id: int) -> Decimal:
        income = self.get_total_income(user_id)
        expense = self.get_total_expense(user_id)

        return income - expense

    def get_statistics(self, user_id: int) -> dict:
        income = self.get_total_income(user_id)
        expense = self.get_total_expense(user_id)

        return {
            "income": income,
            "expense": expense,
            "balance": income - expense,
        }
