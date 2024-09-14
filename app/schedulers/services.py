from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Select, Insert, Result, select, insert, Delete, Update, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ScheduleAlreadyExistsException, ScheduleNotFoundException
from app.schedulers import Schedulers
from app.users.schemas import UserReadSchema


class SchedulerService:
    model = Schedulers

    @classmethod
    async def get_list(cls, session: AsyncSession, user: UserReadSchema, **filters):
        query: Select = select(cls.model).filter_by(**filters, user_id=user.id)
        return await paginate(session, query)

    @classmethod
    async def get_detail(cls, session: AsyncSession, user: UserReadSchema, scheduler_id: int) -> Schedulers:
        query: Select = select(cls.model).filter_by(id=scheduler_id, user_id=user.id)
        scheduler_result: Result[tuple[Schedulers]] = await session.execute(query)
        scheduler_db: Schedulers = scheduler_result.scalar_one_or_none()
        return scheduler_db

    @classmethod
    async def create(cls, session: AsyncSession, user: UserReadSchema, **data) -> Schedulers:
        try:
            stmt: Insert = insert(cls.model).values(**data, user_id=user.id).returning(cls.model)
            scheduler_result: Result[tuple[Schedulers]] = await session.execute(stmt)
            await session.commit()
        except IntegrityError:
            raise ScheduleAlreadyExistsException
        scheduler_db: Schedulers = scheduler_result.scalar_one_or_none()
        return scheduler_db

    @classmethod
    async def update(cls, session: AsyncSession, user: UserReadSchema, scheduler_id, **data) -> Schedulers:
        try:
            stmt: Update = (
                update(cls.model)
                .filter_by(user_id=user.id, id=scheduler_id)
                .values(**data)
                .returning(cls.model)
            )
            scheduler_result: Result = await session.execute(stmt)
            await session.commit()
        except IntegrityError:
            raise ScheduleAlreadyExistsException
        scheduler_db: Schedulers | None = scheduler_result.scalar_one_or_none()
        if not scheduler_db:
            raise ScheduleNotFoundException
        return scheduler_db

    @classmethod
    async def delete(cls, session: AsyncSession, user: UserReadSchema, scheduler_id: int) -> None:
        stmt: Delete = delete(cls.model).filter_by(id=scheduler_id, user_id=user.id)
        await session.execute(stmt)
        await session.commit()
