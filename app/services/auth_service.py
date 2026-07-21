from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token

SECRET_KEY = "very-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


class AuthService:
    password_hash = PasswordHash.recommended()

    def __init__(self, repository: UserRepository | None = None):
        self.repository = repository

    def hash_password(self, password: str) -> str:
        return self.password_hash.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_hash.verify(plain_password, hashed_password)

    def create_access_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {
            "sub": str(user_id),
            "exp": expire,
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    def verify_access_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            user_id = payload.get("sub")

            if user_id is None:
                raise ValueError("Invalid token.")

            return int(user_id)

        except JWTError:
            raise ValueError("Invalid token.")

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