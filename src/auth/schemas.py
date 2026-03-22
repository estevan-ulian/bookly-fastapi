import uuid
from pydantic import BaseModel, Field
from typing import List
from src.books.schemas import BookSchema
from datetime import datetime


class UserSchema(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    password_hash: str = Field(exclude=True)
    created_at: datetime
    updated_at: datetime


class UserBooksSchema(UserSchema):
    books: List[BookSchema]


class UserCreateSchema(BaseModel):
    username: str = Field(min_length=3, max_length=12)
    first_name: str = Field(min_length=3, max_length=24)
    last_name: str = Field(min_length=3, max_length=24)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6, max_length=40)


class UserLoginSchema(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6, max_length=40)
