from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.settings import db_settings
from app.tasks.schemas import TaskListSchema, TaskDetailSchema, TaskBaseCreateSchema
from app.tasks.services import TaskService
from app.users.schemas import UserReadSchema
from app.users.services import UserService

router = APIRouter(
    prefix='/tasks',
    tags=['Tasks']
)


@router.get('/list/', response_model=Page[TaskListSchema])
async def get_list(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                   user: Annotated[UserReadSchema, Depends(UserService.get_current_user)]):
    return await TaskService.task_list(session, user)


@router.get('/detail/{task_id}/', response_model=TaskDetailSchema)
async def get_detail(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                     user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                     task_id: int):
    return await TaskService.task_detail(session, user, task_id)


@router.post('/create/', response_model=TaskDetailSchema)
async def create(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 data: TaskBaseCreateSchema):
    return await TaskService.task_create(session, user, data)


@router.put('/update/{task_id}/', response_model=TaskDetailSchema)
async def update(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 task_id: int,
                 data: TaskBaseCreateSchema):
    return await TaskService.task_update(session, user, task_id, data)


@router.delete('/delete/{task_id}')
async def delete(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 task_id: int):
    await TaskService.task_delete(session, user, task_id)
