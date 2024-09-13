from datetime import datetime, timezone

import jwt
from asyncpg.pgproto.pgproto import timedelta
from fastapi import Request
from itsdangerous import BadSignature
from itsdangerous.url_safe import URLSafeTimedSerializer
from passlib.context import CryptContext
from pydantic import EmailStr

from app.exceptions import URLTokenExpiredOrInvalidException
from app.settings import settings

password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_jwt_token(data: dict, refresh=False):
    to_encode = data.copy()
    if not refresh:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.security.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.security.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, settings.security.JWT_SECRET_KEY, settings.security.JWT_ALGORITHM)
    return encoded_jwt


async def get_access_token(request: Request) -> str | None:
    return request.cookies.get('access_token')


async def get_refresh_token(request: Request) -> str | None:
    return request.cookies.get('refresh_token')


async def get_url_token(email: EmailStr) -> str:
    serializer = URLSafeTimedSerializer(settings.security.VERIFY_URL_SECRET_KEY)
    confirmation_token = serializer.dumps(email)
    return confirmation_token


async def check_url_token(token: str, max_age: int = 3600) -> EmailStr:
    serializer = URLSafeTimedSerializer(secret_key=settings.security.VERIFY_URL_SECRET_KEY)
    try:
        data = serializer.loads(token, max_age=max_age)
    except BadSignature:
        raise URLTokenExpiredOrInvalidException
    return data
