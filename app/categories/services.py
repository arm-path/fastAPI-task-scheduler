from sqlalchemy.ext.asyncio import AsyncSession

from app.categories import Categories
from app.categories.schemas import CategoryCreateUpdateSchema
from app.database.exceptions import ExceptionsDatabase
from app.database.services import DatabaseService
from app.exceptions import (CategoryAlreadyExistsException,
                            NotChangedCategoryDoesNotExistException)
from app.users.schemas import UserReadSchema


class CategoryService(DatabaseService):
    model = Categories

    @classmethod
    async def create_category(cls, session: AsyncSession, user: UserReadSchema, data: CategoryCreateUpdateSchema):
        exceptions = ExceptionsDatabase(unique_error=CategoryAlreadyExistsException)
        return await cls.create(session, exceptions=exceptions, user_id=user.id, **data.model_dump())

    @classmethod
    async def update_category(cls, session: AsyncSession,
                              user: UserReadSchema,
                              category_id: int,
                              data: CategoryCreateUpdateSchema):
        exceptions = ExceptionsDatabase(unique_error=CategoryAlreadyExistsException,
                                        object_not_found=NotChangedCategoryDoesNotExistException)
        return await cls.update(session,
                                filters={'id': category_id, 'user_id': user.id},
                                exceptions=exceptions,
                                title=data.title)

    @classmethod
    async def delete_category(cls, session: AsyncSession, user: UserReadSchema, category_id: int) -> None:
        await cls.delete(session, filters={'id': category_id, 'user_id': user.id})
