import logging
from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.models import ReviewModel
from src.auth.service import UserService
from src.books.service import BookService
from .schemas import ReviewCreateSchema

user_service = UserService()
book_service = BookService()


class ReviewService:
    async def add_review_to_book(self, user_email: str, book_uid: str, review_data: ReviewCreateSchema, session: AsyncSession):
        try:
            book = await book_service.get_book_by_uid(book_uid, session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )
            user = await user_service.get_user_by_email(user_email, session)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            review_data_dict = review_data.model_dump()
            new_review = ReviewModel(**review_data_dict)
            new_review.user = user
            new_review.book = book
            session.add(new_review)
            await session.commit()
            return new_review
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops... Something went wrong"
            )
