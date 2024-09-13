from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.settings import db_settings
from app.users import Users
from app.users.schemas import (RegistrationSchema, AuthenticationSchema, UserRecoveryPasswordSchema,
                               UserRecoveryPasswordEditSchema)
from app.users.services import UserService

router = APIRouter(
    prefix='/authentication',
    tags=['Authentication']
)


@router.post('/registration')
async def registration(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                       user: RegistrationSchema):
    await UserService.registration(session, user)
    return {'detail': {'code': 'success'}}


@router.post('/authorization')
async def authorization(response: Response,
                        session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                        user: AuthenticationSchema) -> None:
    access_token, refresh_token = await UserService.authorization(session, user)
    response.set_cookie('access_token', access_token)
    response.set_cookie('refresh_token', refresh_token)

@router.get('/logout')
async def logout(response: Response):
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')


@router.post('/recovery-password/')
async def recovery_password(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                            data: UserRecoveryPasswordSchema):
    await UserService.recovery_password(session, data.email)
    return {'detail': {'code': 'success'}}


@router.get('/recovery-password/edit/{token}')
async def recovery_password_confirmation(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                                         token: str):
    await UserService.check_url_token(session, token)
    return {'detail': {'code': 'success'}}


@router.post('/recovery-password/edit/{token}')
async def recovery_password_edit(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                                 token: str, data: UserRecoveryPasswordEditSchema):
    await UserService.recovery_password_edit(session, token, data.password1, data.password2)
    return {'detail': {'code': 'success'}}


@router.post('/change-password')
async def change_password(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                          user: Annotated[Users, Depends(UserService.get_current_user)],
                          data: UserRecoveryPasswordEditSchema):
    await UserService.change_password(session, user, data.password1, data.password2)
    return {'detail': {'code': 'success'}}


@router.get('/activate/{token}')
async def confirmation_email_address(session: Annotated[AsyncSession, Depends(db_settings.get_session)],
                                     token: str):
    await UserService.confirmation_email(session, token)
    return {'detail': {'code': 'success'}}


@router.get('/me')
async def get_me(user: Annotated[Users, Depends(UserService.get_current_user)]):
    return user
