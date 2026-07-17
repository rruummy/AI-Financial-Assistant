from app.core.db import SessionLocal
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate

session = SessionLocal()

repo = UserRepository(session)

"""for i in range(10):
    email_pattern = f"test_{i}@example.com"
    name_pattern = f"name_test_{i}"
    user = UserCreate(
            email=email_pattern,
            name=name_pattern,
            password="12w3e4567",
        )
    repo.create(user, "HASH6767")"""
for strings in repo.get_all():
    print(f"{strings.id} | {strings.name} | {strings.email}")