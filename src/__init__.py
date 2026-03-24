from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from src.tags.routes import tags_router
from src.exceptions import register_exceptions
from src.middlewares import register_middlewares
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server is starting...")
    yield
    print("Server has been stopped.")

version = "v1"

app = FastAPI(
    title="Bookly API",
    description="A REST API for a book review web service",
    version=version,
    root_path="/api",
    lifespan=lifespan
)

register_exceptions(app)
register_middlewares(app)


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
