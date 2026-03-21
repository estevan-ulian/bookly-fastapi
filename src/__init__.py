from fastapi import FastAPI
from src.books.routes import book_router
from contextlib import asynccontextmanager
from src.db.main import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Server is starting...")
    await init_db()
    yield
    print(f"Server has been stoped.")

version = "v1"

app = FastAPI(
    title="Bookly API",
    description="A REST API for a book review web service",
    version=version,
    root_path="/api",
    lifespan=lifespan
)

app.include_router(
    book_router,
    prefix=f"/{version}/books",
    tags=["Books"]
)
