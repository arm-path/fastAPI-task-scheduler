from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.database.services import DatabaseService
from app.tasks import Tasks
from app.tasks.schemas import TaskBaseCreateSchema
from app.users.schemas import UserReadSchema


class TaskService(DatabaseService):
    model = Tasks

    @classmethod
    async def task_list(cls, session: AsyncSession, user: UserReadSchema):
        options = [joinedload(cls.model.category), ]
        return await cls.get_list(session, options=options, user_id=user.id, is_paginate=True)

    @classmethod
    async def task_detail(cls, session: AsyncSession, user: UserReadSchema, task_id):
        options = [selectinload(cls.model.category), selectinload(cls.model.scheduler)]
        return await cls.get_detail(session, options=options, user_id=user.id, model_id=task_id)

    @classmethod
    async def task_create(cls, session: AsyncSession, user: UserReadSchema, data: TaskBaseCreateSchema):
        options = [selectinload(cls.model.category), selectinload(cls.model.scheduler)]
        return await cls.create(session, options=options, user_id=user.id, **data.model_dump())

    @classmethod
    async def task_update(cls, session: AsyncSession, user: UserReadSchema, task_id: int, data: TaskBaseCreateSchema):
        options = [selectinload(cls.model.category), selectinload(cls.model.scheduler)]
        return await cls.update(session,
                                filters={'id': task_id, 'user_id': user.id},
                                options=options,
                                **data.model_dump())

    @classmethod
    async def task_delete(cls, session: AsyncSession, user: UserReadSchema, task_id):
        await cls.delete(session, filters={'id': task_id, 'user_id': user.id})
