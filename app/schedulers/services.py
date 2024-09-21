from sqlalchemy.ext.asyncio import AsyncSession

from app.database.exceptions import ExceptionsDatabase
from app.database.services import DatabaseService
from app.exceptions import ScheduleAlreadyExistsException, ScheduleNotFoundException
from app.schedulers import Schedulers
from app.schedulers.schemas import SchedulerCreateUpdateSchema
from app.users.schemas import UserReadSchema


class SchedulerService(DatabaseService):
    model = Schedulers

    @classmethod
    async def create_scheduler(cls, session: AsyncSession,
                               user: UserReadSchema,
                               data: SchedulerCreateUpdateSchema) -> Schedulers:
        exceptions = ExceptionsDatabase(unique_error=ScheduleAlreadyExistsException)
        return await cls.create(session, exceptions=exceptions, user_id=user.id, **data.model_dump())

    @classmethod
    async def update_scheduler(cls, session: AsyncSession,
                               user: UserReadSchema,
                               scheduler_id: int,
                               data: SchedulerCreateUpdateSchema) -> Schedulers:
        exceptions = ExceptionsDatabase(unique_error=ScheduleAlreadyExistsException,
                                        object_not_found=ScheduleNotFoundException)
        return await cls.update(session,
                                filters={'id': scheduler_id, 'user_id': user.id},
                                exceptions=exceptions,
                                **data.model_dump()
                                )

    @classmethod
    async def delete_scheduler(cls, session: AsyncSession, user: UserReadSchema, scheduler_id: int) -> None:
        await cls.delete(session, filters={'id': scheduler_id, 'user_id': user.id})
