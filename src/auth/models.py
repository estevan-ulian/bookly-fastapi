from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
from src.utils import utcnow
import uuid


class UserModel(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    uid: uuid.UUID = Field(sa_column=Column(
        pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    username: str = Field(index=True, unique=True)
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)
    role: str = Field(
        sa_column=Column(
            pg.VARCHAR,
            nullable=False,
            server_default="user"
        )
    )
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            default=utcnow
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            default=utcnow
        )
    )

    def __repr__(self):
        return f"<User {self.username}>"
