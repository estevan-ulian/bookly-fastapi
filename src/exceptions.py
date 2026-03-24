from typing import Any, Callable, Awaitable
from fastapi import FastAPI, status
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


def register_exceptions(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExistsException,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "User with this email already exists",
                "error_code": "USER_EXISTS"
            }
        )
    )

    app.add_exception_handler(
        AccessTokenRequiredException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Get an access token",
                "error_code": "ACCESS_TOKEN_REQUIRED"
            }
        )
    )

    app.add_exception_handler(
        RefreshTokenRequiredException,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Get an refresh token",
                "error_code": "REFRESH_TOKEN_REQUIRED"
            }
        )
    )

    app.add_exception_handler(
        UserNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "USER_NOT_FOUND"
            }
        )
    )

    app.add_exception_handler(
        RevokedTokenException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Token has been revoked",
                "error_code": "TOKEN_REVOKED"
            }
        )
    )

    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid email and password",
                "error_code": "INVALID_CREDENTIALS"
            }
        )
    )

    app.add_exception_handler(
        InsufficientPermissionException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "You are not allowed to perform this action",
                "error_code": "INSUFFICIENT_PERMISSION"
            }
        )
    )

    app.add_exception_handler(
        BookNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book not found",
                "error_code": "BOOK_NOT_FOUND"
            }
        )
    )

    app.add_exception_handler(
        TagAlreadyExistsException,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "A tag with this name alread exists",
                "error_code": "TAG_ALREADY_EXISTS"
            }
        )
    )

    app.add_exception_handler(
        TagNotFoundException,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Tag not found",
                "error_code": "TAG_NOT_FOUND"
            }
        )
    )

    app.add_exception_handler(
        InvalidTokenException,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid token",
                "error_code": "INVALID_TOKEN"
            }
        )
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exception):
        return JSONResponse(
            content={
                "message": "Oops... Something went wrong",
                "error_code": "SERVER_ERROR"
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
