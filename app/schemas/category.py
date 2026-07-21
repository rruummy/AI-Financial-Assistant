from pydantic import BaseModel, ConfigDict, Field
from enum import Enum

class CategoryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class CategoryCreate(BaseModel):
    name: str
    category_type: CategoryType
    
class CategoryUpdate(BaseModel):
    name: str | None = None
    category_type: CategoryType | None = None

class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    category_type: CategoryType = Field(validation_alias="type")
