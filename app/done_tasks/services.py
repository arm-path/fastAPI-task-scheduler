from datetime import date, timedelta
from typing import List

from asyncpg import UniqueViolationError
from sqlalchemy import Select, select, Result, Insert, insert, Update, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.done_tasks import DoneTasks
from app.exceptions import (InvalidTaskIdException,
                            NotAccordingToScheduleException,
                            QuantityCannotNegativeException,
                            UnhandledException,
                            DoneTaskAlreadyExistsException, ObjectNotFoundException, DatesIncorrectException,
                            NotTasksFoundByDateException
                            )
from app.tasks import Tasks
from app.users.schemas import UserReadSchema


class DoneTaskService:
    model = DoneTasks

    @classmethod
    async def create(cls, session: AsyncSession, user: UserReadSchema, **values):
        task_id: int = values.get('task_id')
        task_query: Select = (
            select(Tasks)
            .filter_by(id=task_id, user_id=user.id)
            .options(selectinload(Tasks.scheduler))
        )
        task_result: Result[tuple[Tasks]] = await session.execute(task_query)
        task_db: Tasks | None = task_result.scalar_one_or_none()
        if not task_db:
            raise InvalidTaskIdException
        day_week: str = values.get('date').strftime("%A").lower()
        allowed_day: bool = task_db.scheduler.__dict__.get(day_week)
        if not allowed_day:
            raise NotAccordingToScheduleException
        quantity: int = values.get('quantity')
        if quantity and quantity < 0:
            raise QuantityCannotNegativeException
        try:
            stmt: Insert = (
                insert(cls.model)
                .values(**values)
                .returning(cls.model)
                .options(selectinload(cls.model.task).options(
                    selectinload(Tasks.category), selectinload(Tasks.scheduler))
                )
            )
            done_task_result: Result[tuple[DoneTasks]] = await session.execute(stmt)
            await session.commit()
        except IntegrityError as err:
            if err.orig.__cause__.__class__ == UniqueViolationError:
                raise DoneTaskAlreadyExistsException
            raise UnhandledException
        except Exception as err:
            raise UnhandledException
        done_task_db: DoneTasks = done_task_result.scalar_one_or_none()
        return done_task_db

    @classmethod
    async def update(cls, session: AsyncSession, user: UserReadSchema, done_task_id: int, **values):
        query: Select = (
            select(cls.model)
            .filter_by(id=done_task_id)
            .options(selectinload(cls.model.task))
        )
        done_task_result: Result[tuple[DoneTasks]] = await session.execute(query)
        done_task_db: Tasks | None = done_task_result.scalar_one_or_none()
        if not done_task_db or done_task_db.task.user_id != user.id:
            raise ObjectNotFoundException
        quantity: int = values.get('quantity')
        if quantity and quantity < 0:
            raise QuantityCannotNegativeException

        stmt: Update = (
            update(cls.model)
            .filter_by(id=done_task_id)
            .values(**values)
            .returning(cls.model)
            .options(selectinload(cls.model.task).options(
                selectinload(Tasks.category), selectinload(Tasks.scheduler))
            )
        )
        done_task_result: Result[tuple[DoneTasks]] = await session.execute(stmt)
        await session.commit()
        done_task_db: DoneTasks = done_task_result.scalar_one_or_none()
        return done_task_db

    @classmethod
    async def detail(cls, session: AsyncSession, user: UserReadSchema, done_task_id: int):
        query: Select = (
            select(cls.model)
            .filter_by(id=done_task_id)
            .options(selectinload(cls.model.task).options(
                selectinload(Tasks.category), selectinload(Tasks.scheduler))
            )
        )
        done_task_result: Result[tuple[DoneTasks]] = await session.execute(query)
        done_task_db: DoneTasks | None = done_task_result.scalar_one_or_none()
        if not done_task_db or done_task_db.task.user_id != user.id:
            raise ObjectNotFoundException

        return done_task_db

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
