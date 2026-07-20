from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, PasswordChange
from app.models.user import User
from app.services.auth_service import AuthService

class UserService:
    def __init__(self, repository: UserRepository, auth_service: AuthService):
        self.repository = repository
        self.auth_service = auth_service

    def register(self, user_data: UserCreate) -> User:
        existing_user = self.repository.get_by_email(user_data.email)

        if existing_user :
            raise ValueError("User with this email already exists. Try another email.")

        password_hash = self.auth_service.hash_password(user_data.password)
        user = self.repository.create(user_data=user_data,
                                      password_hash=password_hash,)

        return user

    def get_profile(self, user_id: int) -> User | None:
        return self.repository.get_by_id(user_id)

    def update_profile(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found.")

        if (user_data.email is not None and user_data.email != user.email):
            existing_user = self.repository.get_by_email(user_data.email)

            if existing_user:
                raise ValueError("Email already exists.")
        user.email = user_data.email

        if user_data.password is not None:
            user.password_hash = self.auth_service.hash_password(user_data.password)

        if user_data.name is not None:
            user.password_hash = self.auth_service.hash_password(user_data.password)

        return self.repository.update(user)

    def change_password(self, user_id: int, password_data: PasswordChange) -> User:
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found.")

        if not self.auth_service.verify_password(password_data.old_password, user.password_hash,):
            raise ValueError("Incorect password.")

        user.password_hash = self.auth_service.hash_password(password_data.new_password)
        
        return self.repository.update(user)

    def delete_account(self, user_id: int) -> None:
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise ValueError("User not found.")

        self.repository.delete(user)