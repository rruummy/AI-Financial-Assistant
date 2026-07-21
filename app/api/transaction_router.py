from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_transaction_service
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED,)
def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)):
    try:
        return transaction_service.create_transaction(transaction_data, current_user.id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("", response_model=list[TransactionResponse])
def get_transactions(
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)):
    return transaction_service.get_user_transactions(current_user.id)

@router.get("/category/{category_id}", response_model=list[TransactionResponse])
def get_transactions_by_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)):
    return transaction_service.get_transactions_by_category(current_user.id, category_id)

@router.get("/period", response_model=list[TransactionResponse])
def get_transactions_by_period(
    start_date: datetime,
    end_date: datetime,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)):
    return transaction_service.get_transactions_by_period(current_user.id, start_date, end_date)

@router.get("/statistics/income")
def get_total_income(
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)):
    return {
        "total_income": transaction_service.get_total_income(current_user.id)}

@router.get("/statistics/expense")
def get_total_expense(
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)):
    return {
        "total_expense": transaction_service.get_total_expense(current_user.id)}

@router.get("/statistics/balance")
def get_balance(
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)):
    return {
        "balance": transaction_service.get_balance(current_user.id)}

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)):
    try:
        transaction = transaction_service.get_transaction(transaction_id)

        if transaction.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        return transaction

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)):
    try:
        transaction = transaction_service.get_transaction(transaction_id)

        if transaction.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        return transaction_service.update_transaction(transaction_id, transaction_data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service)):
    try:
        transaction = transaction_service.get_transaction(transaction_id)

        if transaction.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        transaction_service.delete_transaction(transaction_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))