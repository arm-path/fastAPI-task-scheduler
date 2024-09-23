from typing import Annotated

from fastapi import APIRouter, Depends, status
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
    return await CategoryService.get_list(session, is_paginate=True, user_id=user.id)


@router.get('/detail/{category_id}/', response_model=CategoryDetailSchema)
async def get_detail(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                     session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                     category_id: int):
    return await CategoryService.get_detail(session, id=category_id, user_id=user.id)


@router.post('/create/', response_model=CategoryDetailSchema)
async def create(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 data: CategoryCreateUpdateSchema):
    return await CategoryService.create_category(session, user, data)


@router.put('/edit/{category_id}/', response_model=CategoryDetailSchema)
async def edit(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
               session: Annotated[AsyncSession, Depends(db_settings.get_session)],
               category_id: int,
               data: CategoryCreateUpdateSchema):
    return await CategoryService.update_category(session, user, category_id, data)


@router.delete('/delete/{category_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 category_id: int):
    await CategoryService.delete_category(session, user, category_id)
