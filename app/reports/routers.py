from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.settings import db_settings
from app.reports.services import ReportServices
from app.users.schemas import UserReadSchema
from app.users.services import UserService

router = APIRouter(
    prefix='/reports',
    tags=['Reports']
)


@router.get('/', description='Количество выполненных задач')
async def get_tasks_completed(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                              user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                              date_from: date = None, date_to: date = None):
    return await ReportServices.base_report(session, user, date_from, date_to)


@router.get('/percentage-completed/', description='Процент выполненных задач')
async def get_percent_tasks_completed(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                                      user: Annotated[UserReadSchema, Depends(UserService.get_current_user)]):
    return await ReportServices.percent_tasks_completed(session, user)


@router.get('/quantitative-data/')
async def get_quantity_done(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                            user: Annotated[UserReadSchema, Depends(UserService.get_current_user)],
                            date_month: date = None):
    return await ReportServices.quantity_done(session, user, date_month)
