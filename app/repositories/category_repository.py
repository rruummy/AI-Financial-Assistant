from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.category import Category
from app.schemas.category import CategoryCreate

class CategoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, category_data: CategoryCreate) -> Category:
        category = Category(name = category_data.name,
                            type = category_data.type,
                            user_id = category_data.user_id)
        
        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)

        return category

    def get_by_id(self, category_id: int) -> Category | None:
        return self.session.get(Category, category_id)

    def get_by_user(self, user_id: int) -> list[Category]:
        stmt = select(Category).where(Category.user_id == user_id)
        return self.session.scalars(stmt).all()

    def get_by_name(self, user_id: int, category_name: str) -> Category | None:
        stmt = select(Category).where(Category.user_id == user_id,
                                      Category.name == category_name)
        return self.session.scalar(stmt)

    def update(self, category: Category) -> Category:
        self.session.commit()
        self.session.refresh(category)
        return category

    def delete(self, category: Category) -> None:
        self.session.delete(category)
        self.session.commit()