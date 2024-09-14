from typing import List, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.settings import Base

if TYPE_CHECKING:
    from app.tasks.models import Tasks

class Schedulers(Base):
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    monday: Mapped[bool] = mapped_column(Boolean, default=False)
    tuesday: Mapped[bool] = mapped_column(Boolean, default=False)
    wednesday: Mapped[bool] = mapped_column(Boolean, default=False)
    thursday: Mapped[bool] = mapped_column(Boolean, default=False)
    friday: Mapped[bool] = mapped_column(Boolean, default=False)
    saturday: Mapped[bool] = mapped_column(Boolean, default=False)
    sunday: Mapped[bool] = mapped_column(Boolean, default=False)

    tasks: Mapped[List['Tasks']] = relationship(back_populates='scheduler')

    __table_args__ = (
        UniqueConstraint('user_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                         name='uq_days_week'),
        UniqueConstraint('title', 'user_id', name='uq_scheduler_title_user_id')
    )

    def __str__(self):
        return f'<Scheduler {self.id}: {self.title}/>'
