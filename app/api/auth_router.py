from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service, get_user_service, get_current_user
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"],)

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service)):
    try:
        user = user_service.register(user_data)

        token = auth_service.create_access_token(user.id)

        return Token(access_token=token, token_type="bearer")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),):
    try:
        return auth_service.login(
            email=form_data.username,
            password=form_data.password)

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/me")
def me(current_user: UserResponse = Depends(get_current_user)):
    return current_user