from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel import select, desc
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import TagModel
from src.books.service import BookService
from .schemas import TagCreateSchema, TagAddModel

book_service = BookService()


class TagService:
    async def create_tag(self, tag_data: TagCreateSchema, session: AsyncSession):
        """Create a tag"""
        statement = select(TagModel).where(TagModel.name == tag_data.name)
        result = await session.exec(statement)
        tag = result.first()
        if tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This tag name already exists"
            )
        new_tag = TagModel(name=tag_data.name)  # type: ignore
        session.add(new_tag)
        await session.commit()
        return new_tag

    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession):
        """Get a tag by tag_uid"""
        statement = select(TagModel).where(TagModel.uid == tag_uid)
        result = await session.exec(statement)
        tag = result.first()
        return tag if tag is not None else None

    async def get_all_tags(self, session: AsyncSession):
        """Get all tags"""
        statement = select(TagModel).order_by(desc(TagModel.created_at))
        result = await session.exec(statement)
        tags = result.all()
        return tags

    async def add_tag_to_book(self, book_uid: str, tag_data: TagAddModel, session: AsyncSession):
        book = await book_service.get_book_by_uid(book_uid, session)

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        for tag_item in tag_data.tags:
            statement = select(TagModel).where(TagModel.name == tag_item.name)
            result = await session.exec(statement)
            tag = result.one_or_none()
            if not tag:
                tag = TagModel(name=tag_item.name)  # type: ignore

            book.tags.append(tag)

        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book

    async def update_tag(self, tag_uid: str, tag_update_data: TagCreateSchema, session: AsyncSession):
        """Update a tag by its uid"""
        tag_to_update = await self.get_tag_by_uid(tag_uid, session)
        if not tag_to_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")

        tag_update_data_dict = tag_update_data.model_dump()
        for key, value in tag_update_data_dict.items():
            setattr(tag_to_update, key, value)
            await session.commit()
            await session.refresh(tag_to_update)
        return tag_to_update

    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        """Delete a tag by its uid"""
        tag_to_delete = await self.get_tag_by_uid(tag_uid, session)
        if tag_to_delete is not None:
            await session.delete(tag_to_delete)
            await session.commit()
        else:
            return None
