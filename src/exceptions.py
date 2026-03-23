from typing import Any, Callable, Awaitable
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class BooklyException(Exception):
    """This is the base class for all bookly exceptions"""
    pass


class InvalidTokenException(BooklyException):
    """User has provided an invalid or expired token"""
    pass


class RevokedTokenException(BooklyException):
    """User has provided a token that has been revoked"""
    pass


class AccessTokenRequiredException(BooklyException):
    """"User has provided a refresh token when an access token is needed"""
    pass


class RefreshTokenRequiredException(BooklyException):
    """User has provided an access token when a refresh token is needed"""
    pass


class UserAlreadyExistsException(BooklyException):
    """User has provided an email for a user who exists during sign up"""
    pass


class UserNotFoundException(BooklyException):
    """"User not found"""
    pass


class InvalidCredentials(BooklyException):
    """User provided an invalid email or password during login"""


class InsufficientPermissionException(BooklyException):
    """User does not have the necessary permissions to perform this action"""
    pass


class BookNotFoundException(BooklyException):
    """Book not found"""
    pass


class TagAlreadyExistsException(BooklyException):
    """The provided tag name already exists"""
    pass


class TagNotFoundException(BooklyException):
    """Tag not found"""
    pass


def create_exception_handler(
    status_code: int,
    initial_detail: Any
) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def exception_handler(request: Request, exception: BooklyException):
        return JSONResponse(
            content=initial_detail,
            status_code=status_code,
        )

    return exception_handler  # type: ignore
