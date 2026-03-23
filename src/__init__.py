from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.tags.routes import tags_router
from src.exceptions import (
    create_exception_handler,
    AccessTokenRequiredException,
    TagAlreadyExistsException,
    BookNotFoundException,
    InvalidTokenException,
    InvalidCredentials,
    InsufficientPermissionException,
    RefreshTokenRequiredException,
    TagNotFoundException,
    RevokedTokenException,
    UserAlreadyExistsException,
    UserNotFoundException,

)
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting...")
    # await init_db()
    yield
    print("Server has been stoped.")

version = "v1"

app = FastAPI(
    title="Bookly API",
    description="A REST API for a book review web service",
    version=version,
    root_path="/api",
    lifespan=lifespan
)

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

app.include_router(
    book_router,
    prefix=f"/{version}/books",
    tags=["books"]
)
app.include_router(
    auth_router,
    prefix=f"/{version}/auth",
    tags=["auth"]
)
app.include_router(
    review_router,
    prefix=f"/{version}/reviews",
    tags=["reviews"]
)
app.include_router(
    tags_router,
    prefix=f"/{version}/tags",
    tags=["tags"]
)
