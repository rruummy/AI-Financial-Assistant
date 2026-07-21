from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_category_service, get_current_user
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),):
    try:
        return category_service.create_category(category_data, current_user.id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("", response_model=list[CategoryResponse])
def get_categories(
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service),):
    return category_service.get_user_category(current_user.id)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service)):
    try:
        category = category_service.get_by_id(category_id)

        if category.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        return category

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service)):
    try:
        category = category_service.get_by_id(category_id)

        if category.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        return category_service.update_category(category_id, category_data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    category_service: CategoryService = Depends(get_category_service)):
    try:
        category = category_service.get_by_id(category_id)

        if category.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        category_service.delete_category(category_id)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))