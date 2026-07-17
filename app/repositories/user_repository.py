from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.user import User
from app.schemas.user import UserCreate

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, user_data: UserCreate, password_hash: str) -> User:
        user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash,
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user
    
    def get_by_id(self, user_id: int) -> User | None:
        return self.session.get(User, user_id)
    
    def get_by_email(self, user_email: str) -> User | None:
        stmt = select(User).where(User.email == user_email)
        return self.session.scalar(stmt)

    def get_all(self) -> list:
        stmt = select(User)
        return list(self.session.scalars(stmt))

    def update(self, user: User) -> User:
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()
