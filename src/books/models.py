from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, date
from src.utils import utcnow
from typing import Optional
from src.auth import models
import uuid


class BookModel(SQLModel, table=True):
    __tablename__ = "books"  # type: ignore

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.uid",
    )
    created_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            default=utcnow,
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            pg.TIMESTAMP(timezone=True),
            default=utcnow,
        ))
    user: Optional["models.UserModel"] = Relationship(back_populates="books")

    def __repr__(self):
        return f"<Book {self.title}>"
