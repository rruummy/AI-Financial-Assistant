from pydantic import BaseModel
from enum import Enum

class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class CategoryCreate(BaseModel):
    name: str
    category_type: CategoryType
    
class CategoryUpdate(BaseModel):
    name: str
    category_type: CategoryType

class CategoryResponse(BaseModel):
    id: int
    name: str
    category_type: CategoryType
