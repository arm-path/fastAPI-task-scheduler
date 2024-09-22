from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.settings import db_settings
from app.done_tasks.schemas import CrateDoneTaskSchema, UpdateDoneTaskSchema
from app.done_tasks.services import DoneTaskService
from app.users.schemas import UserReadSchema
from app.users.services import UserService

router = APIRouter(
    prefix='/list-tasks',
    tags=['List Tasks']
)


@router.post('/create/')
async def create(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 data: CrateDoneTaskSchema):
    return await DoneTaskService.done_task_create(session, user, data)


@router.post('/update/{done_task_id}')
async def update(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 done_task_id: int,
                 data: UpdateDoneTaskSchema):
    return await DoneTaskService.task_update(session, user, done_task_id, **data.model_dump())


@router.get('/detail/{done_task_id}/')
async def detail(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 done_task_id: int):
    return await DoneTaskService.done_task_detail(session, user, done_task_id)


@router.get('/list/tasks/')
async def scheduler_tasks(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                          user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                          date_start: date, date_end: date):
    return await DoneTaskService.get_tasks(session, user, date_start, date_end)
