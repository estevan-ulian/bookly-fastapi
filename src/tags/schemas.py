import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class TagSchema(BaseModel):
    uid: uuid.UUID
    name: str = Field(max_length=20)
    created_at: datetime
    updated_at: datetime


class TagCreateSchema(BaseModel):
    name: str


class TagAddModel(BaseModel):
    tags: List[TagCreateSchema]
