from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.db import SessionLocal

from app.models.user import User

from app.repositories.user_repository import UserRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.ai_chat_repository import AIChatRepository

from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.category_service import CategoryService
from app.services.transaction_service import TransactionService
from app.services.ai_service import AIService
from app.services.llm_service import LLMService


# DATABASE 

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# REPOSITORIES

def get_user_repository(
    db: Session = Depends(get_db),
):
    return UserRepository(db)


def get_category_repository(
    db: Session = Depends(get_db),
):
    return CategoryRepository(db)


def get_transaction_repository(
    db: Session = Depends(get_db),
):
    return TransactionRepository(db)


def get_ai_chat_repository(
    db: Session = Depends(get_db),
):
    return AIChatRepository(db)


# SERVICES

def get_auth_service(repository: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repository)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
    auth_service: AuthService = Depends(get_auth_service),
):
    return UserService(repository, auth_service)


def get_category_service(
    repository: CategoryRepository = Depends(get_category_repository),
):
    return CategoryService(repository)


def get_transaction_service(
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
    category_repository: CategoryRepository = Depends(get_category_repository),
):
    return TransactionService(
        transaction_repository,
        category_repository,
    )


def get_llm_service():
    return LLMService()


def get_ai_service(
    ai_repository: AIChatRepository = Depends(get_ai_chat_repository),
    transaction_service: TransactionService = Depends(get_transaction_service),
    category_service: CategoryService = Depends(get_category_service),
    llm_service: LLMService = Depends(get_llm_service),
):
    return AIService(
        ai_repository,
        transaction_service,
        category_service,
        llm_service,
    )


# AUTH

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:

    try:
        return auth_service.get_current_user(token)

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )