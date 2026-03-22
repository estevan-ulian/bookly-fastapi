import uuid
import sqlalchemy.dialects.postgresql as pg
from sqlmodel import SQLModel, Column, Relationship, Field
from datetime import datetime, date
from typing import Optional, List
from src.utils import utcnow


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
    books: List["BookModel"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            'lazy': 'selectin'
        }
    )
    reviews: List["ReviewModel"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            'lazy': 'selectin'
        }
    )

    def __repr__(self):
        return f"<User {self.username}>"


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
    user: Optional["UserModel"] = Relationship(back_populates="books")
    review: List["ReviewModel"] = Relationship(back_populates="book")

    def __repr__(self):
        return f"<Book {self.title}>"


class ReviewModel(SQLModel, table=True):
    __tablename__ = "reviews"  # type: ignore

    uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID,
            nullable=False,
            primary_key=True,
            default=uuid.uuid4
        )
    )
    rating: int = Field(lt=5)
    review_text: str = Field(max_length=255)
    user_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="users.uid",
    )
    book_uid: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="books.uid",
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
    user: Optional["UserModel"] = Relationship(back_populates="reviews")
    book: Optional["BookModel"] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for book '{self.book_uid}' by user '{self.user_uid}'.>"
