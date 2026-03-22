import uuid
from typing import List
from pydantic import BaseModel
from datetime import datetime, date
from src.reviews.schemas import ReviewSchema


class BookSchema(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookDetailSchema(BookSchema):
    reviews: List[ReviewSchema]


class BookCreateSchema(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookUpdateSchema(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    language: str
