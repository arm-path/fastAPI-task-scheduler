from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Select, select, Result, Insert, insert, Update, update, Delete, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories import Categories
from app.exceptions import (CategoryAlreadyExistsException, NotChangedCategoryDoesNotExistException,
                            FailedDeleteCategoryException)
from app.users.schemas import UserReadSchema


class CategoryService:
    model = Categories

    @classmethod
    async def get_list(cls, session: AsyncSession, user: UserReadSchema, **filters):
        query: Select = select(cls.model).filter_by(user_id=user.id, **filters)
        return await paginate(session, query)

    @classmethod
    async def get_detail(cls, session: AsyncSession, user: UserReadSchema, category_id: int) -> Categories:
        query: Select = select(cls.model).filter_by(user_id=user.id, id=category_id)
        category_result: Result[tuple[Categories]] = await session.execute(query)
        category_db: Categories = category_result.scalar_one_or_none()
        return category_db

    @classmethod
    async def create(cls, session: AsyncSession, user: UserReadSchema, **values) -> Categories:
        try:
            query: Insert = insert(cls.model).values(user_id=user.id, **values).returning(cls.model)
            category_result: Result[tuple[Categories]] = await session.execute(query)
            await session.commit()
            category_db: Categories = category_result.scalar_one_or_none()
        except IntegrityError:
            raise CategoryAlreadyExistsException
        return category_db

    @classmethod
    async def update(cls, session: AsyncSession, user: UserReadSchema, category_id: int, title: str) -> Categories:
        try:
            query: Update = (
                update(cls.model).filter_by(id=category_id, user_id=user.id).values(title=title).returning(cls.model)
            )
            category_result: Result[tuple[Categories]] = await session.execute(query)
            await session.commit()
        except IntegrityError:
            raise CategoryAlreadyExistsException
        category_db: Categories | None = category_result.scalar_one_or_none()
        if not category_db:
            raise NotChangedCategoryDoesNotExistException
        return category_db

    @classmethod
    async def delete(cls, session: AsyncSession, user: UserReadSchema, category_id: int) -> None:
        try:
            query: Delete = delete(cls.model).filter_by(id=category_id, user_id=user.id)
            await session.execute(query)
            await session.commit()
        except Exception as e:
            raise FailedDeleteCategoryException
