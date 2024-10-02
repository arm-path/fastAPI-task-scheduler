from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

from app.settings import settings
from app.utils import camel_case_to_snake_case


class DatabaseSettings:
    def __init__(self, echo=settings.database.ENGINE_ECHO):
        self.engine = create_async_engine(
            settings.POSTGRES_URL if settings.VERSION == 'PROD' else settings.database.POSTGRES_URL, echo=echo
        )
        self.session = async_sessionmaker(self.engine, expire_on_commit=False, autoflush=False)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session() as session_db:
            yield session_db

    async def dispose(self):  # Завершение.
        await self.engine.dispose()


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)
    metadata = MetaData(naming_convention=settings.database.CONVENTION)

    @declared_attr
    def __tablename__(cls):
        return camel_case_to_snake_case(cls.__name__)


db_settings = DatabaseSettings()
