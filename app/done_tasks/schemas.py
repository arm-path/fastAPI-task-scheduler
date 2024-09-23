from datetime import date, datetime

from pydantic import BaseModel

from app.tasks.schemas import TaskDetailSchema


class BaseDoneTaskSchema(BaseModel):
    quantity: int = 0
    is_done: bool = False


class EditDoneTaskSchema(BaseDoneTaskSchema):
    date: date
    task_id: int


class DoneTasksDetail(BaseDoneTaskSchema):
    date: date
    update: datetime
    id: int
    task: TaskDetailSchema


class DoneTaskSchedulerSchema(BaseModel):
    date: date
    quantity: int
    is_done: bool
    # updated: datetime


class TaskSchedulerSchema(BaseModel):
    id: int
    title: str
    start_date: date
    end_date: date
    quantity: int
    quantity_unit: str


class DoneTasksListSchema(BaseModel):
    task: TaskSchedulerSchema
    done: DoneTaskSchedulerSchema | dict = {}
