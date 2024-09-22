from datetime import date, datetime

from pydantic import BaseModel

from app.categories.schemas import CategoryListSchema
from app.schedulers.schemas import SchedulerDetailSchema


class TaskBaseSchema(BaseModel):
    title: str
    start_date: date
    end_date: date
    quantity: int
    quantity_unit: str


class TaskBaseCreateSchema(TaskBaseSchema):
    category_id: int | None
    scheduler_id: int | None


class TaskListSchema(TaskBaseSchema):
    id: int
    category: CategoryListSchema


class TaskDetailSchema(TaskListSchema):
    id: int
    scheduler: SchedulerDetailSchema
    created: datetime
    updated: datetime
