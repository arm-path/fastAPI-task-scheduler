from typing import Sequence

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Select, select, Result, Insert, insert, Update, update, Delete, delete
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.exceptions import ExceptionsDatabase, integrity_error_handling
from app.exceptions import (ObjectNotFoundException, UnhandledException, DatabaseQueryErrorException)


class DatabaseService:
    model = None

    @classmethod
    async def get_list(cls, session: AsyncSession, is_paginate: bool = False, options: list = [], **filters):
        query: Select = (
            select(cls.model)
            .filter_by(**filters)
            .options(*options)
        )
        if is_paginate:
            return await paginate(session, query)
        result: Result[tuple[cls.model]] = await session.execute(query)
        data: Sequence[cls.model] = result.scalars().all()
        return data

    @classmethod
    async def get_detail(cls, session: AsyncSession, options: list = [], is_none=False, **filters):
        try:
            query: Select = (
                select(cls.model)
                .filter_by(**filters)
                .options(*options)
            )
            result: Result[tuple[cls.model]] = await session.execute(query)
        except InvalidRequestError as err:
            raise DatabaseQueryErrorException
        except Exception as err:
            raise UnhandledException
        data: cls.model = result.scalar_one_or_none()
        if not data and not is_none:
            raise ObjectNotFoundException
        return data

    @classmethod
    async def create(cls,
                     session: AsyncSession,
                     exceptions: ExceptionsDatabase = ExceptionsDatabase(),
                     options: list = [],
                     **values):
        try:
            stmt: Insert = (
                insert(cls.model)
                .values(**values)
                .returning(cls.model)
                .options(*options)
            )
            result: Result[cls.model] = await session.execute(stmt)
            await session.commit()
            return result.scalar_one_or_none()
        except IntegrityError as err:
            raise integrity_error_handling(err, exceptions)
        except InvalidRequestError as err:
            raise DatabaseQueryErrorException
        except Exception as err:
            raise UnhandledException

    @classmethod
    async def update(cls,
                     session: AsyncSession,
                     filters: dict,
                     exceptions: ExceptionsDatabase = ExceptionsDatabase(),
                     options: list = [],
                     **values):
        try:
            stmt: Update = (
                update(cls.model)
                .filter_by(**filters)
                .values(**values)
                .returning(cls.model)
                .options(*options)
            )
            result: Result[cls.model] = await session.execute(stmt)
            await session.commit()
            data = result.scalar_one_or_none()
            if not data:
                if exceptions.object_not_found:
                    raise exceptions.object_not_found
                else:
                    raise ObjectNotFoundException
            return data
        except IntegrityError as err:
            raise integrity_error_handling(err, exceptions)
        except InvalidRequestError as err:
            raise DatabaseQueryErrorException
        except Exception as err:
            raise UnhandledException

    @classmethod
    async def delete(cls, session: AsyncSession, filters: dict):
        try:
            stmt: Delete = (
                delete(cls.model)
                .filter_by(**filters)
            )
            await session.execute(stmt)
            await session.commit()
        except InvalidRequestError as err:
            raise DatabaseQueryErrorException
        except Exception as err:
            print(err)
            raise UnhandledException
