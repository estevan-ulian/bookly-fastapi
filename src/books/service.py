import uuid
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from .schemas import BookUpdateSchema, BookCreateSchema
from .models import BookModel
from datetime import datetime


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(BookModel).order_by(desc(BookModel.created_at))
        result = await session.exec(statement)
        books = result.all()
        return books

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = select(BookModel).where(
            BookModel.user_uid == user_uid).order_by(desc(BookModel.created_at))
        result = await session.exec(statement)
        books = result.all()
        return books

    async def get_book_by_uid(self, book_uuid, session: AsyncSession):
        statement = select(BookModel).where(BookModel.uid == book_uuid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None

    async def create_book(self, book_data: BookCreateSchema, user_uid: uuid.UUID, session: AsyncSession):
        book_data_dict = book_data.model_dump()
        new_book = BookModel(
            **book_data_dict,
        )
        new_book.user_uid = user_uid

        new_book.published_date = datetime.strptime(
            book_data_dict["published_date"], "%Y-%m-%d").date()

        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(self, book_id, update_data: BookUpdateSchema, session: AsyncSession):
        book_to_update = await self.get_book_by_uid(book_id, session)
        if book_to_update is not None:
            update_data_dict = update_data.model_dump()
            for key, value in update_data_dict.items():
                setattr(book_to_update, key, value)
            await session.commit()
            return book_to_update
        else:
            return None

    async def delete_book(self, book_id, session: AsyncSession):
        book_to_delete = await self.get_book_by_uid(book_id, session)
        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
        else:
            return None
