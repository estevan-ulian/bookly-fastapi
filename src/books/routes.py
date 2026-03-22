from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from typing import List
from src.books.schemas import BookSchema, BookCreateSchema, BookUpdateSchema
from src.books.service import BookService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import AccessTokenBearer, RoleChecker

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(allowed_roles=["admin", "user"])


@book_router.get("/", response_model=List[BookSchema], dependencies=[Depends(role_checker)])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer)
):
    print(token_details)
    books = await book_service.get_all_books(session)
    return books


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=BookSchema, dependencies=[Depends(role_checker)])
async def create_book(
    book_data: BookCreateSchema,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer)
):
    new_book = await book_service.create_book(book_data, session)
    return new_book


@book_router.get("/{book_uuid}", response_model=BookSchema, dependencies=[Depends(role_checker)])
async def get_book(
    book_uuid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer)
):
    book = await book_service.get_book_by_uid(book_uuid, session)
    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.patch("/{book_uuid}", response_model=BookSchema, dependencies=[Depends(role_checker)])
async def update_book(
    book_uuid: str,
    book_update_data: BookUpdateSchema,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer)
):
    updated_book = await book_service.update_book(book_uuid, book_update_data, session)
    if updated_book:
        return updated_book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@book_router.delete("/{book_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_uuid: str, session: AsyncSession = Depends(get_session), token_details=Depends(access_token_bearer)):
    book_to_delete = await book_service.delete_book(book_uuid, session)
    if book_to_delete is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    else:
        return {"detail": "Book deleted successfully"}
