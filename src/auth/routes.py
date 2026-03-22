from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta
from src.db.main import get_session
from .schemas import UserCreateSchema, UserSchema, UserLoginSchema
from .services import UserService
from .utils import create_access_token, verify_password


auth_router = APIRouter()
user_service = UserService()

REFRESH_ACCESS_TOKEN_EXPIRY_DAYS = 7


@auth_router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")
    new_user = await user_service.create_user(user_data, session)
    return new_user


@auth_router.post("/login")
async def login_users(user_login_data: UserLoginSchema, session: AsyncSession = Depends(get_session)):
    email = user_login_data.email
    password = user_login_data.password

    user = await user_service.get_user_by_email(email, session)
    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_id': str(user.uid)
                },
            )

            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_id': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_ACCESS_TOKEN_EXPIRY_DAYS)
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "email": user.email,
                        "uid": str(user.uid)
                    }
                }
            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
    )
