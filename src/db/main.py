from sqlmodel import create_engine, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker

from src.config import Config

async_engine = AsyncEngine(
    create_engine(
        url=Config.DATABASE_URL,
        echo=True,
    )
)


async def init_db():
    async with async_engine.begin() as connection:
        from src.books.models import BookModel  # noqa: F401
        from src.auth.models import UserModel  # noqa: F401

        await connection.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with Session() as session:
        yield session
