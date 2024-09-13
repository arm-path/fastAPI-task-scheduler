from datetime import date

from sqlalchemy import String, text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.settings import Base


class Users(Base):
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hash_password: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(server_default=text('false'))
    created: Mapped[date] = mapped_column(nullable=False, default=func.current_date())

    def __str__(self):
        return f'<User {self.id}: {self.username}/>'
