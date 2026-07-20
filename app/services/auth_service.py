from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from passlib.context import CryptContext
from app.repositories.user_repository import UserRepository

SECRET_KEY = "very-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, secret_key: str,
                 algorithm: str = "HS256",
                 access_token_expire_minutes: int = 30):
        self.password_hash = PasswordHash.recommended()
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
    
    def hash_password(self, password: str) -> str:
        return self.password_hash.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.password_hash.verify(plain_password, hashed_password)
    
    def create_access_token(self, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)

        payload = {
            "sub": str(user_id),
            "exp": expire,
        }

        token = jwt.encode(payload, self.secret_key, algorithm = self.algorithm)

        return token

    def verify_access_token(self, token: str) -> int:
        payload = jwt.decode(self.secret_key, algorithms=[self.algorithm])
        return int(payload("sub"))

    def login(self, repository: UserRepository, email: str, password: str) -> str:
        user = repository.get_by_email(email)

        if user is None:
            raise ValueError("Incorrect email or password.")

        if not self.verify_password(password, user.password_hash):
            raise ValueError("Incorrect email or password.")

        return self.create_access_token(user.id)
   