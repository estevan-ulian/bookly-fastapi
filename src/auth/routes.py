from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi_mail import NameEmail
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import timedelta, datetime, timezone
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist
from src.config import Config
from src.worker import send_email
from .service import UserService
from .utils import create_access_token, verify_password, create_url_safe_token, decode_url_safe_token, generate_password_hash
from .schemas import (
    UserCreateSchema,
    UserCreateResponseSchema,
    UserLoginSchema,
    UserBooksSchema,
    PasswordResetRequestSchema,
    PasswordResetConfirmSchema
)
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    RoleChecker,
    get_current_user
)
from src.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentials,
    InvalidTokenException,
    UserNotFoundException,
    PasswordsDoNotMatchException
)
from src.mail import create_message


auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(allowed_roles=["admin", "user"])

REFRESH_ACCESS_TOKEN_EXPIRY_DAYS = 7


@auth_router.post("/signup", response_model=UserCreateResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_user_account(user_data: UserCreateSchema, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    user_exists = await user_service.user_exists(email, session)
    if user_exists:
        raise UserAlreadyExistsException()
    new_user = await user_service.create_user(user_data, session)
    token = create_url_safe_token({"email": email})
    verify_link = f"http://{Config.APP_DOMAIN}/api/v1/auth/verify/{token}"
    html_message = f"""
        <h1>Welcome to the App, {email}!</h1>
        <p>Thank you for signing up. We're excited to have you on board!</p><br>
        <p>Please, verify your email address by clicking the link below:</p><br>
        <a href="{verify_link}">Verify Email</a>
    """
    message = create_message(
        recipients=[NameEmail(name=new_user.first_name, email=new_user.email)],
        subject="Welcome! Verify your email!",
        body=html_message
    )
    send_email.delay(message)
    return {
        "success": True,
        "message": "Account created! Please check your email to verify your account.",
        "user": new_user
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = decode_url_safe_token(token)
    if not token_data:
        raise InvalidTokenException()
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFoundException()

        await user_service.update_user({"is_verified": True}, user, session)

        return JSONResponse(
            content={
                "success": True,
                "message": "Account verified successfully"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={
            "success": False,
            "message": "An error occurred during account verification. Please, try again later."
        },
        status_code=status.HTTP_400_BAD_REQUEST
    )


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
    raise InvalidCredentials()


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

    raise InvalidTokenException()


@auth_router.get("/me", response_model=UserBooksSchema)
async def get_current_user_details(user=Depends(get_current_user), _: bool = Depends(role_checker)):
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):
    jti = token_details["jti"]
    await add_jti_to_blocklist(jti)
    return JSONResponse(
        content={
            "message": "Logged out successfuly",
        },
        status_code=status.HTTP_200_OK
    )


@auth_router.post("/reset_password")
async def reset_password(email_data: PasswordResetRequestSchema):
    email = email_data.email
    token = create_url_safe_token({"email": email})
    verify_link = f"http://{Config.APP_DOMAIN}/api/v1/reset_password_confirm/{token}"
    html_message = f"""
        <h1>Reset your password!</h1>
        <p>We received a request to reset your password. Click the link below to proceed:</p><br>
        <a style='padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px;' href="{verify_link}">Reset Password</a>
    """
    message = create_message(
        recipients=[NameEmail(name="", email=email)],
        subject="Password Reset Request",
        body=html_message
    )
    send_email.delay(message)
    return JSONResponse(
        content={
            "success": True,
            "message": "Password reset email sent. Please check your email to proceed.",
        },
        status_code=status.HTTP_200_OK
    )


@auth_router.post("/reset_password_confirm/{token}")
async def reset_password_confirm(token: str, passwords: PasswordResetConfirmSchema, session: AsyncSession = Depends(get_session)):
    new_password = passwords.new_password
    new_password_confirm = passwords.new_password_confirm
    if new_password != new_password_confirm:
        raise PasswordsDoNotMatchException()

    token_data = decode_url_safe_token(token)
    if not token_data:
        raise InvalidTokenException()
    user_email = token_data.get("email")
    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFoundException()

        password_hash = generate_password_hash(new_password)
        await user_service.update_user({"password_hash": password_hash}, user, session)

        return JSONResponse(
            content={
                "success": True,
                "message": "Password reset successfully"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={
            "success": False,
            "message": "An error occurred during password reset. Please, try again later."
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
