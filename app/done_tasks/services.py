from datetime import date, timedelta
from typing import List

from sqlalchemy import Select, select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.database.exceptions import ExceptionsDatabase
from app.database.services import DatabaseService
from app.done_tasks import DoneTasks
from app.done_tasks.schemas import CrateDoneTaskSchema
from app.exceptions import (InvalidTaskIdException,
                            NotAccordingToScheduleException,
                            QuantityCannotNegativeException,
                            DoneTaskAlreadyExistsException, ObjectNotFoundException, DatesIncorrectException,
                            NotTasksFoundByDateException
                            )
from app.tasks import Tasks
from app.tasks.services import TaskService
from app.users.schemas import UserReadSchema


class DoneTaskService(DatabaseService):
    model = DoneTasks

    @classmethod
    async def done_task_create(cls, session: AsyncSession, user: UserReadSchema, data: CrateDoneTaskSchema):
        task_db: Tasks | None = await TaskService.task_detail(session, user, data.task_id)
        if not task_db:
            raise InvalidTaskIdException
        day_week: str = data.date.strftime("%A").lower()
        allowed_day: bool = task_db.scheduler.__dict__.get(day_week)
        if not allowed_day:
            raise NotAccordingToScheduleException
        quantity: int = data.quantity
        if quantity and quantity < 0:
            raise QuantityCannotNegativeException
        options = [
            selectinload(cls.model.task).options(selectinload(Tasks.category), selectinload(Tasks.scheduler))
        ]
        exceptions = ExceptionsDatabase(unique_error=DoneTaskAlreadyExistsException)
        return await cls.create(session, options=options, exceptions=exceptions, **data.model_dump())

    @classmethod
    async def task_update(cls, session: AsyncSession, user: UserReadSchema, done_task_id: int, data):
        options = [selectinload(cls.model.task)]
        done_task_db = await cls.get_detail(session, options=options, model_id=done_task_id)
        if not done_task_db or done_task_db.task.user_id != user.id:
            raise ObjectNotFoundException
        quantity: int = data.quantity
        if quantity and quantity < 0:
            raise QuantityCannotNegativeException

        options = [
            selectinload(cls.model.task).options(selectinload(Tasks.category), selectinload(Tasks.scheduler))]
        return await cls.update(session, filters={'id': done_task_id}, options=options, **data.model_dump())

    @classmethod
    async def done_task_detail(cls, session: AsyncSession, user: UserReadSchema, done_task_id: int):
        options = [
            selectinload(cls.model.task).options(selectinload(Tasks.category), selectinload(Tasks.scheduler))
        ]
        done_task: cls.model | None = await cls.get_detail(session, options=options, model_id=done_task_id)
        if done_task.task.user_id != user.id:
            raise ObjectNotFoundException
        return done_task

    @classmethod
    async def get_tasks(cls, session: AsyncSession, user: UserReadSchema, date_start: date, date_end: date):
        if date_start > date_end:
            raise DatesIncorrectException

        query_tasks: Select = (
            select(Tasks)
            .where(Tasks.user_id == user.id, Tasks.end_date > date_start, Tasks.start_date < date_end)
            .options(joinedload(Tasks.scheduler))
        )
        tasks_result: Result[tuple[Tasks]] = await session.execute(query_tasks)
        tasks_db = tasks_result.scalars().all()
        if not tasks_db:
            raise NotTasksFoundByDateException(date_start, date_end)

        allowed_tasks_ids: List[int] = [el.id for el in tasks_db]

        query_done_tasks: Select = (
            select(cls.model)
            .where(cls.model.id.in_(allowed_tasks_ids),
                   cls.model.date > date_start, cls.model.date < date_end)
        )
        done_tasks_result: Result[tuple[DoneTasks]] = await session.execute(query_done_tasks)
        done_tasks_db = done_tasks_result.scalars().all()

        current_date: date = date_start
        tasks = {}
        while current_date <= date_end:
            day_week: str = current_date.strftime("%A").lower()
            tasks_in_date = []
            tasks[current_date] = tasks_in_date
            for task in tasks_db:
                allowed_day: bool = task.scheduler.__dict__.get(day_week)
                if allowed_day:
                    tasks_in_date.append({'task': task, 'done': {}})
            tasks[current_date] = tasks_in_date
            current_date += timedelta(days=1)

        for done_task in done_tasks_db:
            find_task = tasks.get(done_task.date)
            if find_task:
                for el in tasks[done_task.date]:
                    if el['task'].id == done_task.id:
                        el['done'] = done_task.__dict__
        return tasks
