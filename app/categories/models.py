from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.settings import Base

if TYPE_CHECKING:
    from app.users.models import Users


class Categories(Base):
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    user: Mapped['Users'] = relationship(back_populates='categories')

    __table_args__ = (UniqueConstraint('title', 'user_id', name='uq_title_user_id'), )

    def __str__(self):
        return f'<Category {self.id}: {self.title} />'
