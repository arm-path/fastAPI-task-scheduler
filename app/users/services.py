from typing import Annotated

import jwt
from fastapi import Depends, Response
from jwt import InvalidTokenError, ExpiredSignatureError
from pydantic import EmailStr
from sqlalchemy import select, or_, insert, update, Result, Update, Insert, Select
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer

from app.database.settings import db_settings
from app.exceptions import (UserAlreadyExistsException,
                            UserOrPasswordEnteredIncorrectException,
                            UserNotAuthorizedException, URLTokenExpiredOrInvalidException,
                            UserAlreadyActivatedException, EmailAddressIsNotRegisteredException,
                            PasswordsNotMatchException)
from app.settings import settings
from app.tasks.users import send_mail_recovery_password, send_mail_email_confirmation
from app.users.models import Users
from app.users.schemas import RegistrationSchema, AuthenticationSchema, JWTPyloadSchema
from app.users.utils import (get_hash_password, verify_password, create_access_jwt_token, get_access_token,
                             get_refresh_token, get_url_token, check_url_token)


class UserService:
    model = Users

    @classmethod
    async def registration(cls, session: AsyncSession, user: RegistrationSchema) -> int:
        try:
            query_user: Select = (
                select(cls.model).where(or_(cls.model.email == user.email, cls.model.username == user.username))
            )
            db_user: Result[tuple[Users]] = await session.execute(query_user)
            user_exists: Users | None = db_user.scalar_one_or_none()
        except MultipleResultsFound as e:
            raise UserAlreadyExistsException
        if user_exists:
            raise UserAlreadyExistsException
        hash_password: str = get_hash_password(user.password)
        stmt: Insert = insert(cls.model).values(
            username=user.username,
            email=user.email,
            hash_password=hash_password
        ).returning(cls.model.id)
        user_result: Result[tuple[Users]] = await session.execute(stmt)
        await session.commit()
        user_id: int | None = user_result.scalars().one_or_none()
        token = await get_url_token(user.email)
        send_mail_email_confirmation(user.email, token)
        return user_id

    @classmethod
    async def confirmation_email(cls, session: AsyncSession, token: str) -> None:
        db_user: Users = await cls.check_url_token(session, token, 3600 * 24)
        if db_user.active:
            raise UserAlreadyActivatedException
        stmt_user: Update = update(cls.model).where(cls.model.email == db_user.email).values(active=True)
        await session.execute(stmt_user)
        await session.commit()

    @classmethod
    async def authorization(cls, session: AsyncSession, user: AuthenticationSchema) -> tuple:
        try:
            query_user: Select = (
                select(cls.model).where(or_(cls.model.email == user.username, cls.model.username == user.username))
            )
            db_user: Result[tuple[Users]] = await session.execute(query_user)
            db_user: Users | None = db_user.scalar_one_or_none()
        except MultipleResultsFound:
            raise UserOrPasswordEnteredIncorrectException
        if db_user is None:
            raise UserOrPasswordEnteredIncorrectException
        if not verify_password(user.password, db_user.hash_password):
            raise UserOrPasswordEnteredIncorrectException
        data_token = {'id': str(db_user.id)}
        access_token: str = create_access_jwt_token(data_token)
        refresh_token: str = create_access_jwt_token(data_token, refresh=True)
        return access_token, refresh_token

    @classmethod
    async def get_user_db(cls,
                          session: Annotated[AsyncSession, db_settings.get_session],
                          user_id: int) -> Users:
        query: Select = select(cls.model).where(cls.model.id == int(user_id)).options(defer(cls.model.hash_password))
        user_db: Result[tuple[Users]] = await session.execute(query)
        user_db: Users | None = user_db.scalar_one_or_none()
        if not user_db or not user_db.active:
            raise UserNotAuthorizedException
        return user_db

    @classmethod
    async def get_current_user(cls, response: Response,
                               session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                               access_token: Annotated[str | None, Depends(get_access_token)],
                               refresh_token: Annotated[str | None, Depends(get_refresh_token)]) -> Users:
        if not access_token:
            raise UserNotAuthorizedException
        try:
            access_payload: JWTPyloadSchema = jwt.decode(access_token,
                                                         settings.security.JWT_SECRET_KEY,
                                                         algorithms=[settings.security.JWT_ALGORITHM])
        except ExpiredSignatureError:
            if not refresh_token:
                raise UserNotAuthorizedException
            try:
                refresh_payload: JWTPyloadSchema = jwt.decode(refresh_token,
                                                              settings.security.JWT_SECRET_KEY,
                                                              algorithms=[settings.security.JWT_ALGORITHM])
            except InvalidTokenError as e:
                raise UserNotAuthorizedException
            user_id: str = refresh_payload.get('id')
            user_db: Users = await cls.get_user_db(session, int(user_id))
            data_token = {'id': str(user_db.id)}
            access_token: str = create_access_jwt_token(data_token)
            response.set_cookie('access_token', access_token)
            return await cls.get_current_user(response, session, access_token, refresh_token)
        except InvalidTokenError as e:
            raise UserNotAuthorizedException

        user_id: str = access_payload.get('id')
        if not user_id or not user_id.isdigit():
            raise UserNotAuthorizedException
        return await cls.get_user_db(session, int(user_id))

    @classmethod
    async def recovery_password(cls, session: AsyncSession, email: EmailStr) -> None:
        query: Select = select(cls.model).where(cls.model.email == email)
        user_result: Result[tuple[Users]] = await session.execute(query)
        users_db: Users | None = user_result.scalar_one_or_none()
        if not users_db or not users_db.active:
            raise EmailAddressIsNotRegisteredException
        confirmation_token: str = await get_url_token(email)
        send_mail_recovery_password(email, users_db.username, confirmation_token)  # TODO: Task library.

    @classmethod
    async def check_url_token(cls, session: AsyncSession, token: str, max_age: int = 3600) -> Users:
        email: EmailStr = await check_url_token(token, max_age)
        try:
            query_user: Select = (select(cls.model).where(cls.model.email == email))
            db_user: Result[tuple[Users]] = await session.execute(query_user)
            db_user: Users | None = db_user.scalar_one_or_none()
        except:
            raise URLTokenExpiredOrInvalidException
        if not db_user:
            raise URLTokenExpiredOrInvalidException
        return db_user

    @classmethod
    async def recovery_password_edit(cls, session: AsyncSession, token: str, password1: str, password2: str) -> None:
        db_user: Users = await cls.check_url_token(session, token)
        if password1 != password2:
            raise PasswordsNotMatchException
        hash_password: str = get_hash_password(password1)
        stmt: Update = update(cls.model).where(cls.model.id == db_user.id).values(hash_password=hash_password)
        await session.execute(stmt)
        await session.commit()

    @classmethod
    async def change_password(cls, session: AsyncSession, user: Users, password1: str, password2: str) -> None:
        if password1 != password2:
            raise PasswordsNotMatchException
        hash_password: str = get_hash_password(password1)
        stmt: Update = update(cls.model).where(cls.model.id == user.id).values(hash_password=hash_password)
        await session.execute(stmt)
        await session.commit()
