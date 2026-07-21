from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def create_category(self, category_data: CategoryCreate, user_id: int) -> Category:
        existing_category = self.repository.get_by_name_and_type(
            user_id=user_id,
            category_name=category_data.name,
            category_type=category_data.category_type)

        if existing_category:
            raise ValueError("Category aldready exists.")

        return self.repository.create(category_data, user_id)

    def get_by_id(self, category_id: int) -> Category:
        category = self.repository.get_by_id(category_id)

        if category is None:
            raise ValueError("Category not found.")
        
        return category

    def get_user_category(self, user_id: int) -> list[Category]:
        return self.repository.get_by_user(user_id)

    def update_category(self, category_id: int, category_data: CategoryUpdate) -> Category:
        category = self.repository.get_by_id(category_id)

        if category is None:
            raise ValueError("Category not found.")

        new_name = category_data.name if category_data.name is not None else category.name
        new_type = category_data.category_type if category_data.category_type is not None else category.type

        if new_name != category.name or new_type != category.type:
            existing_category = self.repository.get_by_name_and_type(
                user_id=category.user_id,
                category_name=new_name,
                category_type=new_type)

            if existing_category is not None and existing_category.id != category_id:
                raise ValueError(f"Category with name '{new_name}' already exists.")

        category.name = new_name
        category.type = new_type

        return self.repository.update(category)

    def delete_category(self, category_id: int) -> None:
        category = self.repository.get_by_id(category_id)

        if category is None:
            raise ValueError("Category not found.")

        self.repository.delete(category)