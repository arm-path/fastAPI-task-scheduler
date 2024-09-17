from asyncpg import UniqueViolationError
from sqlalchemy import Select, select, Result, Insert, insert, Update, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.done_tasks import DoneTasks
from app.exceptions import (InvalidTaskIdException,
                            NotAccordingToScheduleException,
                            QuantityCannotNegativeException,
                            UnhandledException,
                            DoneTaskAlreadyExistsException, ObjectNotFoundException
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
