from app.core.db import SessionLocal
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate

session = SessionLocal()

repo = UserRepository(session)

"""user = repo.create(
    UserCreate(
        email="test2@test.com",
        name="TR1",
        password="12345678",
    ),
    password_hash="HASH123456",
)

print(user.id)"""
data = repo.get_by_email("new@test.com")
if data:
    print(f"new: {data.name} | {data.email}")
else: print("There's not user with this email.")

repo.delete(data)
data = repo.get_by_email("new@test.com")
if data:
    print(f"new: {data.name} | {data.email}")
else: print("There's not user with this email.")