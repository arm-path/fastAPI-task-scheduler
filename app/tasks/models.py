from datetime import date, datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import String, ForeignKey, Integer, Date, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.settings import Base

if TYPE_CHECKING:
    from app.users.models import Users
    from app.categories.models import Categories
    from app.schedulers.models import Schedulers
    from app.done_tasks.models import DoneTasks


class Tasks(Base):
    title: Mapped[str] = mapped_column(String(65), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    scheduler_id: Mapped[int] = mapped_column(ForeignKey('schedulers.id', ondelete='SET NULL'), nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    quantity_unit: Mapped[str] = mapped_column(String(31), nullable=True)
    created: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"))
    updated: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)

    user: Mapped['Users'] = relationship(back_populates='tasks')
    category: Mapped['Categories'] = relationship(back_populates='tasks')
    scheduler: Mapped['Schedulers'] = relationship(back_populates='tasks')
    done_tasks: Mapped[List['DoneTasks']] = relationship(back_populates='task')

    def __str__(self):
        return f'<Tasks {self.id}: {self.title}/>'
