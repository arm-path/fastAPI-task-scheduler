from datetime import date
from typing import Annotated, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.settings import db_settings
from app.done_tasks.schemas import EditDoneTaskSchema, DoneTasksListSchema
from app.done_tasks.services import DoneTaskService
from app.users.schemas import UserReadSchema
from app.users.services import UserService

router = APIRouter(
    prefix='/list-tasks',
    tags=['List Tasks']
)


@router.post('/edit/')
async def edit_task(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                    user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                    data: EditDoneTaskSchema):
    return await DoneTaskService.done_task_edit(session, user, data)


@router.get('/detail/{done_task_id}/')
async def detail(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                 user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                 done_task_id: int):
    return await DoneTaskService.done_task_detail(session, user, done_task_id)


@router.get('/list/tasks/', response_model=Dict[date, List[DoneTasksListSchema]])
async def scheduler_tasks(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                          user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                          date_start: date = None, date_end: date = None):
    return await DoneTaskService.get_tasks(session, user, date_start, date_end)