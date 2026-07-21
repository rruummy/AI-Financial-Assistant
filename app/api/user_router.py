from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_user_service
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate, PasswordChange
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)):
    try:
        return user_service.update_profile(current_user.id, user_data)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)):
    try:
        user_service.change_password(current_user.id, password_data)
        return {"message": "Password changed successfully."}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/me",status_code=status.HTTP_204_NO_CONTENT)
def delete_account(current_user: User = Depends(get_current_user), user_service: UserService = Depends(get_user_service)):
    try:
        user_service.delete_account(current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))