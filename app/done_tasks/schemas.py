from datetime import date, datetime

from pydantic import BaseModel

from app.tasks.schemas import TaskDetailSchema


class BaseDoneTaskSchema(BaseModel):
    quantity: int = 0
    is_done: bool = False


class CrateDoneTaskSchema(BaseDoneTaskSchema):
    date: date
    task_id: int


class UpdateDoneTaskSchema(BaseDoneTaskSchema):
    pass


class DoneTasksDetail(BaseDoneTaskSchema):
    date: date
    update: datetime
    id: int
    task: TaskDetailSchema


"""
	
{
  "quantity": 0,
  "date": "2024-09-17",
  "is_done": true,
  "id": 1,
  "task_id": 1,
  "updated": "2024-09-17T17:26:20.535199",
  "task": {
    "user_id": 7,
    "category_id": 2,
    "start_date": "2024-09-16",
    "quantity": 0,
    "created": "2024-09-16T17:07:15.789708",
    "id": 1,
    "title": "Программирование FastAPI",
    "scheduler_id": 4,
    "end_date": "2024-12-30",
    "quantity_unit": "",
    "updated": "2024-09-16T17:07:15.789708",
    "scheduler": {
      "tuesday": true,
      "title": "Каждый день",
      "thursday": true,
      "saturday": true,
      "id": 4,
      "user_id": 7,
      "monday": true,
      "wednesday": true,
      "friday": true,
      "sunday": true
    },
    "category": {
      "title": "Обучение",
      "user_id": 7,
      "id": 2
    }
  }
}
"""
