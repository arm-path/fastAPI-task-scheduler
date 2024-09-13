from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.schemas import CategoryListSchema, CategoryDetailSchema, CategoryCreateUpdateSchema
from app.categories.services import CategoryService
from app.database.settings import db_settings
from app.users.schemas import UserReadSchema
from app.users.services import UserService

router = APIRouter(
    prefix='/categories',
    tags=['Categories']
)


@router.get('/list/', response_model=Page[CategoryListSchema])
async def get_list(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                   session: Annotated[AsyncSession, Depends(db_settings.get_session)]):
    categories = await CategoryService.get_list(session, user)
    return categories


@router.get('/detail/{category_id}/', response_model=CategoryDetailSchema)
async def get_detail(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                     session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                     category_id: int):
    return await CategoryService.get_detail(session, user, category_id)


@router.post('/create/', response_model=CategoryDetailSchema)
async def create(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 data: CategoryCreateUpdateSchema):
    return await CategoryService.create(session, user, title=data.title)


@router.put('/edit/{category_id}/')
async def edit(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
               session: Annotated[AsyncSession, Depends(db_settings.get_session)],
               category_id: int,
               data: CategoryCreateUpdateSchema):
    return await CategoryService.update(session, user, category_id, data.title)


@router.delete('/delete/{category_id}/')
async def delete(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 category_id: int):
    await CategoryService.delete(session, user, category_id)
