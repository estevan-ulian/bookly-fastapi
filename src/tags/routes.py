from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from src.db.main import get_session
from src.auth.dependencies import RoleChecker
from .service import TagService
from .schemas import TagSchema, TagCreateSchema, TagAddModel

tags_router = APIRouter()
tag_service = TagService()
role_checker = RoleChecker(allowed_roles=['user', 'admin'])


@tags_router.get(
    "/",
    response_model=List[TagSchema],
    dependencies=[
        Depends(role_checker)
    ]
)
async def get_all_tags(
    session: AsyncSession = Depends(get_session)
):
    all_tags = await tag_service.get_all_tags(session)
    return all_tags


@tags_router.post(
    "/",
    response_model=TagSchema,
    dependencies=[
        Depends(role_checker)
    ]
)
async def create_a_tag(
    tag_data: TagCreateSchema,
    session: AsyncSession = Depends(get_session)
):
    new_tag = await tag_service.create_tag(tag_data, session)
    return new_tag


@tags_router.post(
    "/book/{book_uid}/tags",
    dependencies=[
        Depends(role_checker)
    ]
)
async def add_tags_to_book(
    book_uid: str,
    tag_data: TagAddModel,
    session: AsyncSession = Depends(get_session)
):
    tag_added = await tag_service.add_tag_to_book(book_uid, tag_data, session)
    return tag_added


@tags_router.put(
    "/{tag_uid}",
    dependencies=[
        Depends(role_checker)
    ]
)
async def update_tag(
    tag_uid: str,
    tag_update_data: TagCreateSchema,
    session: AsyncSession = Depends(get_session)
):
    updated_tag = await tag_service.update_tag(tag_uid, tag_update_data, session)
    return updated_tag


@tags_router.delete(
    "/{tag_uid}",
    dependencies=[
        Depends(role_checker)
    ]
)
async def delete_tag(
    tag_uid: str,
    session: AsyncSession = Depends(get_session)
):
    tag_to_delete = await tag_service.delete_tag(tag_uid, session)
    if tag_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    else:
        return JSONResponse(
            content={
                "success": True,
                "detail": "Tag deleted successfuly"
            },
            status_code=status.HTTP_200_OK
        )
