from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import insert, Insert, Result, Select, select, Update, update, Delete, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.base.exceptions import integrity_error_handling
from app.exceptions import UnhandledException
from app.tasks import Tasks
from app.users.schemas import UserReadSchema


class TaskService:
    model = Tasks

    @classmethod
    async def get_list(cls, session: AsyncSession, user: UserReadSchema):
        query: Select = (
            select(cls.model)
            .filter_by(user_id=user.id)
            .options(joinedload(cls.model.category)))

        return await paginate(session, query)

    @classmethod
    async def get_detail(cls, session: AsyncSession, user: UserReadSchema, task_id):
        query: Select = (
            select(cls.model)
            .filter_by(id=task_id, user_id=user.id)
            .options(selectinload(cls.model.category), selectinload(cls.model.scheduler))
        )
        task_result: Result[tuple[Tasks]] = await session.execute(query)
        task_db: Tasks | None = task_result.scalar_one_or_none()
        return task_db

    @classmethod
    async def create(cls, session: AsyncSession, user: UserReadSchema, **data):
        try:
            stmt: Insert = (
                insert(cls.model)
                .values(**data, user_id=user.id)
                .returning(cls.model)
                .options(selectinload(cls.model.category), selectinload(cls.model.scheduler))
            )
            task_result: Result[tuple[Tasks]] = await session.execute(stmt)
        except IntegrityError as err:
            raise integrity_error_handling(err)
        except Exception as err:
            raise UnhandledException
        await session.commit()
        return task_result.scalar_one_or_none()

    @classmethod
    async def update(cls, session: AsyncSession, user: UserReadSchema, task_id: int, **data):
        try:
            stmt: Update = (
                update(cls.model)
                .filter_by(id=task_id, user_id=user.id)
                .values(**data)
                .returning(cls.model)
                .options(selectinload(cls.model.category), selectinload(cls.model.scheduler))
            )
            task_result: Result[tuple[Tasks]] = await session.execute(stmt)
        except IntegrityError as err:
            raise integrity_error_handling(err)
        except Exception as err:
            raise UnhandledException
        await session.commit()
        return task_result.scalar_one_or_none()

    @classmethod
    async def delete(cls, session: AsyncSession, user: UserReadSchema, task_id):
        try:
            stmt: Delete = (
                delete(cls.model)
                .filter_by(id=task_id, user_id=user.id)
            )
            await session.execute(stmt)
            await session.commit()
        except Exception as err:
            raise UnhandledException
