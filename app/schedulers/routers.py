from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.settings import db_settings
from app.schedulers.schemas import SchedulerListSchema, SchedulerDetailSchema, SchedulerCreateUpdateSchema
from app.schedulers.services import SchedulerService
from app.users.schemas import UserReadSchema
from app.users.services import UserService

router = APIRouter(
    prefix='/schedulers',
    tags=['Schedulers']
)


@router.get('/list/', response_model=Page[SchedulerListSchema])
async def get_list(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                   session: Annotated[AsyncSession, Depends(db_settings.get_session)]):
    return await SchedulerService.get_list(session, user_id=user.id, is_paginate=True)


@router.get('/detail/{scheduler_id}', response_model=SchedulerDetailSchema)
async def get_detail(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                     session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                     scheduler_id: int):
    return await SchedulerService.get_detail(session, id=scheduler_id, user_id=user.id)


@router.post('/create/', response_model=SchedulerDetailSchema)
async def create(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 data: SchedulerCreateUpdateSchema):
    return await SchedulerService.create_scheduler(session, user, data)


@router.put('/update/{scheduler_id}', response_model=SchedulerDetailSchema)
async def update(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 data: SchedulerCreateUpdateSchema, scheduler_id: int):
    return await SchedulerService.update_scheduler(session, user, scheduler_id, data)


@router.delete('/delete/{scheduler_id}/')
async def delete(user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 scheduler_id:int):
    await SchedulerService.delete_scheduler(session, user, scheduler_id)
