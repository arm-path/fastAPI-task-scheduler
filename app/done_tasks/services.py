from datetime import date, timedelta
from typing import List

from sqlalchemy import Select, select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.database.exceptions import ExceptionsDatabase
from app.database.services import DatabaseService
from app.done_tasks import DoneTasks
from app.done_tasks.schemas import EditDoneTaskSchema
from app.exceptions import (InvalidTaskIdException,
                            NotAccordingToScheduleException,
                            QuantityCannotNegativeException,
                            DoneTaskAlreadyExistsException, ObjectNotFoundException, DatesIncorrectException,
                            NotTasksFoundByDateException
                            )
from app.tasks import Tasks
from app.tasks.services import TaskService
from app.users.schemas import UserReadSchema


class DoneTaskService(DatabaseService):
    model = DoneTasks

    @classmethod
    async def done_task_edit(cls, session: AsyncSession, user: UserReadSchema, data: EditDoneTaskSchema):
        options = [selectinload(cls.model.task)]
        done_task_db = await cls.get_detail(session,
                                            options=options,
                                            is_none=True,
                                            date=data.date,
                                            task_id=data.task_id)
        if done_task_db and done_task_db.task.user_id != user.id:
            raise InvalidTaskIdException
        if not done_task_db:
            return await cls.done_task_create(session, user, data)
        quantity: int = data.quantity
        if quantity and quantity < 0:
            raise QuantityCannotNegativeException
        options = [
            selectinload(cls.model.task).options(selectinload(Tasks.category), selectinload(Tasks.scheduler))
        ]
        return await cls.update(session, filters={'id': done_task_db.id}, options=options, **data.model_dump())

    @classmethod
    async def done_task_create(cls, session: AsyncSession, user: UserReadSchema, data: EditDoneTaskSchema):
        task_db: Tasks | None = await TaskService.task_detail(session, user, data.task_id)
        if not task_db:
            raise InvalidTaskIdException
        day_week: str = data.date.strftime("%A").lower()
        allowed_day: bool = task_db.scheduler.__dict__.get(day_week)
        if not allowed_day:
            raise NotAccordingToScheduleException
        quantity: int = data.quantity
        if quantity and quantity < 0:
            raise QuantityCannotNegativeException
        options = [
            selectinload(cls.model.task).options(selectinload(Tasks.category), selectinload(Tasks.scheduler))
        ]
        exceptions = ExceptionsDatabase(unique_error=DoneTaskAlreadyExistsException)
        return await cls.create(session, options=options, exceptions=exceptions, **data.model_dump())

    @classmethod
    async def done_task_detail(cls, session: AsyncSession, user: UserReadSchema, done_task_id: int):
        options = [
            selectinload(cls.model.task).options(selectinload(Tasks.category), selectinload(Tasks.scheduler))
        ]
        done_task: cls.model | None = await cls.get_detail(session, options=options, id=done_task_id)
        if done_task.task.user_id != user.id:
            raise ObjectNotFoundException
        return done_task

    @classmethod
    async def get_tasks(cls, session: AsyncSession,
                        user: UserReadSchema,
                        task_id: int,
                        category_id: int,
                        is_done: bool,
                        date_start: date,
                        date_end: date):
        query_task_filter = [Tasks.user_id == user.id]
        query_done_task_filter = []

        if task_id:
            query_task_filter.append(Tasks.id == task_id)
        if category_id:
            query_task_filter.append(Tasks.category_id == category_id)

        not_task_found_args = [date_start, date_end]
        current_date = date.today()
        if date_start and date_end:
            if date_start > date_end:
                raise DatesIncorrectException
            not_task_found_args = [date_start, date_end]
            query_task_filter.extend([Tasks.end_date > date_start, Tasks.start_date < date_end])
            query_done_task_filter = [cls.model.date >= date_start, cls.model.date <= date_end]
        if date_start and not date_end:
            not_task_found_args = [date_start, date_start]
            query_task_filter.extend(
                [Tasks.user_id == user.id, Tasks.start_date < date_start, Tasks.end_date > date_start])
            query_done_task_filter = [cls.model.date == date_start]
            current_date = date_start
        if not date_start and date_end:
            not_task_found_args = [date_end, date_end]
            query_task_filter.extend([Tasks.user_id == user.id, Tasks.start_date < date_end, Tasks.end_date > date_end])
            query_done_task_filter = [cls.model.date == date_end]
            current_date = date_end
        if not date_start and not date_end:
            not_task_found_args = [date.today(), date.today()]
            query_task_filter = [Tasks.user_id == user.id, Tasks.start_date < date.today(),
                                 Tasks.end_date > date.today()]
            query_done_task_filter = [cls.model.date == date.today()]

        query_tasks: Select = (
            select(Tasks)
            .where(*query_task_filter)
            .options(joinedload(Tasks.scheduler), joinedload(Tasks.category))
        )
        tasks_result: Result[tuple[Tasks]] = await session.execute(query_tasks)
        tasks_db = tasks_result.scalars().all()
        if not tasks_db:
            raise NotTasksFoundByDateException(*not_task_found_args)

        allowed_tasks_ids: List[int] = [el.id for el in tasks_db]
        query_done_tasks: Select = (
            select(cls.model)
            .where(cls.model.task_id.in_(allowed_tasks_ids), *query_done_task_filter)
        )
        done_tasks_result: Result[tuple[DoneTasks]] = await session.execute(query_done_tasks)
        done_tasks_db = done_tasks_result.scalars().all()

        if date_start and date_end:
            current_date: date = date_start
        else:
            current_date = current_date
            date_end = current_date
        tasks = {}
        while current_date <= date_end:
            day_week: str = current_date.strftime("%A").lower()
            tasks_in_date = []
            tasks[current_date] = tasks_in_date
            for task in tasks_db:
                allowed_day: bool = task.scheduler.__dict__.get(day_week)
                if allowed_day:
                    tasks_in_date.append({'task': task, 'done': {}})
            tasks[current_date] = tasks_in_date
            current_date += timedelta(days=1)

        for done_task in done_tasks_db:
            find_task = tasks.get(done_task.date)
            if find_task:
                for el in tasks[done_task.date]:
                    if el['task'].id == done_task.task_id:
                        el['done'] = done_task.__dict__
        is_done_tasks = tasks.copy()
        if is_done:
            tasks = {}
            for key, items in is_done_tasks.items():
                tasks_in_date = []
                for item in items:
                    if item['done'].get('is_done'):
                        tasks_in_date.append(item)
                        tasks[key] = tasks_in_date
        if not is_done and not is_done is None:
            tasks = {}
            for key, items in is_done_tasks.items():
                tasks_in_date = []
                for item in items:
                    if not item['done'].get('is_done'):
                        tasks_in_date.append(item)
                        tasks[key] = tasks_in_date
        return tasks
