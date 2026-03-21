from sqlmodel import SQLModel, Field, Column
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime
import uuid


class UserModel(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(sa_column=Column(
        pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4))
    username: str = Field(index=True, unique=True)
    first_name: str
    last_name: str
    email: str = Field(index=True, unique=True)
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.utcnow))
    updated_at: datetime = Field(sa_column=Column(
        pg.TIMESTAMP(timezone=True), default=datetime.utcnow))

    def __repr__(self):
        return f"<User {self.username}>"
