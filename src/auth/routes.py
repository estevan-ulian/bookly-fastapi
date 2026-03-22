from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime, timezone
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from .schemas import UserCreateSchema, UserSchema, UserLoginSchema, UserBooksSchema
from .services import UserService
from .utils import create_access_token, verify_password
from .dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(allowed_roles=["admin", "user"])

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
                    'user_id': str(user.uid),
                    'role': user.role
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


@auth_router.get("/refresh_token")
async def refresh_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details['exp']

    if datetime.fromtimestamp(expiry_timestamp, tz=timezone.utc) > datetime.now(timezone.utc):
        new_access_token = create_access_token(
            user_data=token_details['user']
        )

        return JSONResponse(
            content={
                "access_token": new_access_token
            }
        )

    raise HTTPException(
        status_code=status.HTTP_403_UNAUTHORIZED, detail="Refresh token has expired. Please log in again."
    )


@auth_router.get("/me", response_model=UserBooksSchema)
async def get_current_user_details(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    return user


@auth_router.get("/logout")
async def logout_users(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={
            "message": "Logged out successfuly",
        },
        status_code=status.HTTP_200_OK
    )
