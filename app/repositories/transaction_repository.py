from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate
from app.models.category import Category, CategoryType
from datetime import datetime
from decimal import Decimal

class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, transaction_data: TransactionCreate) -> Transaction:
        transaction = Transaction(
            amount = transaction_data.amount,
            description = transaction_data.description,
            category_id = transaction_data.category_id,
            user_id = transaction_data.user_id,
        )
        self.session.add(transaction)
        self.session.commit()
        self.session.refresh(transaction)

        return transaction

    def get_by_id(self, transaction_id: int) -> Transaction | None:
        return self.session.get(Transaction, transaction_id)

    def get_by_user(self, user_id: int) -> list[Transaction]:
        stmt = select(Transaction).where(Transaction.user_id == user_id)
        return self.session.scalars(stmt).all()

    def update(self, transaction: Transaction) -> Transaction:
        self.session.commit()
        self.session.refresh(transaction)
        return transaction

    def delete(self, transaction: Transaction) -> None:
        self.session.delete(transaction)
        self.session.commit()

    def get_by_category(self, user_id: int, category_id: int) -> list[Transaction]:
        stmt = (select(Transaction)
                .where(Transaction.user_id == user_id,
                       Transaction.category_id == category_id))
        return self.session.scalars(stmt).all()

    def get_by_period(self, user_id: int, start_date: datetime, end_date: datetime) -> list[Transaction]:
        stmt = (select(Transaction)
            .where(Transaction.user_id == user_id,
            Transaction.date.between(start_date, end_date)))
        return self.session.scalars(stmt).all()

    def get_total_income(self, user_id: int) -> Decimal:
        stmt = (select(func.sum(Transaction.amount))
                .join(Category)
                .where(Transaction.user_id == user_id,
                       Category.type == CategoryType.INCOME))

        return self.session.scalar(stmt) or Decimal("0")
    
    def get_total_expense(self, user_id: int) -> Decimal:
        stmt = (select(func.sum(Transaction.amount))
                .join(Category)
                .where(Transaction.user_id == user_id,
                       Category.type == CategoryType.EXPENSE))

        return self.session.scalar(stmt) or Decimal("0")