from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, Date, Boolean, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.settings import Base

if TYPE_CHECKING:
    from app.tasks.models import Tasks

class DoneTasks(Base):
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    updated: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), onupdate=datetime.utcnow)

    task: Mapped['Tasks'] = relationship(back_populates='done_tasks')

    __table_args__ = (UniqueConstraint('task_id', 'date', name='uq_task_id_date'),)

    def __str__(self):
        return f'<DoneTasks {self.id}: {self.task_id}-{self.date}/>'
