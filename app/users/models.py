from datetime import date
from typing import TYPE_CHECKING, List
from sqlalchemy import String, text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.settings import Base

if TYPE_CHECKING:
    from app.categories.models import Categories
    from app.tasks.models import Tasks


class Users(Base):
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hash_password: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(server_default=text('false'))
    created: Mapped[date] = mapped_column(nullable=False, default=func.current_date())

    categories: Mapped[List['Categories']] = relationship(back_populates='user')
    tasks: Mapped[List['Tasks']] = relationship(back_populates='user',
                                                cascade='save-update, merge, delete',
                                                passive_deletes=True)

    def __str__(self):
        return f'<User {self.id}: {self.username}/>'
