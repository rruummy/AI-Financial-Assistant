from app.core import security
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token


class AuthService:
    def __init__(self, repository: UserRepository | None = None):
        self.repository = repository

    def hash_password(self, password: str) -> str:
        return security.hash_password(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return security.verify_password(plain_password, hashed_password)

    def create_access_token(self, user_id: int) -> str:
        return security.create_access_token(user_id)

    def verify_access_token(self, token: str) -> int:
        return security.decode_access_token(token)

    def authenticate_user(self, email: str, password: str) -> User:
        if self.repository is None:
            raise ValueError("Repository is not configured.")

        user = self.repository.get_by_email(email)

        if user is None:
            raise ValueError("Incorrect email or password.")

        if not self.verify_password(password, user.password_hash):
            raise ValueError("Incorrect email or password.")

        return user

    def login(self, email: str, password: str) -> Token:
        user = self.authenticate_user(email, password)

        token = self.create_access_token(user.id)

        return Token(
            access_token=token,
            token_type="bearer",
        )

    def get_current_user(self, token: str) -> User:
        if self.repository is None:
            raise ValueError("Repository is not configured.")

        user_id = self.verify_access_token(token)

        user = self.repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found.")

        return user
