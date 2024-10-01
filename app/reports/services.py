from datetime import date, timedelta

from sqlalchemy import Select, select, Result, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.services import DatabaseService
from app.done_tasks import DoneTasks
from app.exceptions import ParamDatesMustBeDefinedException
from app.reports.utils import get_date_month
from app.tasks import Tasks
from app.users.schemas import UserReadSchema


class ReportServices(DatabaseService):
    model = DoneTasks

    @classmethod
    async def base_report(cls, session: AsyncSession, user: UserReadSchema, date_from, date_to):
        if (date_from and not date_to) or (not date_from and date_to):
            raise ParamDatesMustBeDefinedException
        if not date_from and not date_to:
            date_from, date_to = get_date_month()

        select_fields = [func.count(DoneTasks.id)]
        filters = [DoneTasks.is_done == True, ]
        return await cls.select_tasks_by_group(user, session, date_from, date_to, select_fields, filters)

    @classmethod
    async def percent_tasks_completed(cls, session: AsyncSession, user: UserReadSchema):
        date_from, date_to = get_date_month()
        task_db = await cls.select_tasks_by_timedelta(user, session, date_from, date_to, [])
        tasks_needs_done = await cls.get_tasks_needs_done(task_db, date_from, date_to, quantity=False)
        tasks_done = await cls.base_report(session, user, None, None)
        results = []
        for task_need_done in tasks_needs_done:
            task = task_need_done.copy()
            task['done'] = 0
            for title, key in tasks_done.items():
                if task_need_done.get('title') == title:
                    task['done'] = key
            task['percent_done'] = round(task['done'] / task['need'] * 100, 2)
            results.append(task)

        return results

    @classmethod
    async def quantity_done(cls, session: AsyncSession, user: UserReadSchema, date_month: date):
        date_from, date_to = get_date_month(date_month)
        filters = [Tasks.quantity > 0]
        task_db = await cls.select_tasks_by_timedelta(user, session, date_from, date_to, filters)
        tasks_needs_done = await cls.get_tasks_needs_done(task_db, date_from, date_to, quantity=True)

        select_fields = [func.sum(DoneTasks.quantity)]
        filters = [Tasks.quantity > 0]
        tasks = await cls.select_tasks_by_group(user, session, date_from, date_to, select_fields, filters)

        results = []
        for task_need_done in tasks_needs_done:
            task = task_need_done.copy()
            task['done'] = 0
            for title, key in tasks.items():
                if task_need_done.get('title') == title:
                    task['done'] = key
            task['remainder'] = task['need'] - task['done']
            results.append(task)
        return results

    @classmethod
    async def select_tasks_by_group(cls, user: UserReadSchema,
                                    session: AsyncSession,
                                    date_from: date,
                                    date_to: date,
                                    select_fields: list,
                                    filters: list):
        query_tasks: Select = (
            select(Tasks.title, *select_fields)
            .join(DoneTasks, Tasks.id == DoneTasks.task_id)
            .where(
                DoneTasks.date >= date_from,
                DoneTasks.date <= date_to,
                *filters,
                Tasks.user_id == user.id
            )
            .group_by(Tasks.title)
        )

        result_tasks: Result[tuple[Tasks]] = await session.execute(query_tasks)
        db_tasks = result_tasks.all()
        tasks: dict[str, int] = {}
        for title, count in db_tasks:
            tasks[title] = count
        return tasks

    @classmethod
    async def select_tasks_by_timedelta(cls, user: UserReadSchema,
                                        session: AsyncSession,
                                        date_from: date,
                                        date_to: date,
                                        filters: list):
        query: Select = (
            select(Tasks)
            .where(and_(*filters, Tasks.user_id == user.id,
                        or_(and_(Tasks.start_date >= date_from, Tasks.start_date <= date_to),
                            and_(Tasks.start_date <= date_from, Tasks.end_date > date_from))))
            .options(joinedload(Tasks.scheduler))
        )
        query_result: Result[tuple[Tasks]] = await session.execute(query)
        return query_result.scalars().all()

    @classmethod
    async def get_tasks_needs_done(cls, task_db, date_from: date, date_to: date, quantity: bool):
        tasks_needs_done = []
        for task in task_db:
            task_needs_done = {'title': task.title}
            required = 0
            task_date_from = max(task.start_date, date_from)
            task_date_to = min(task.end_date, date_to)
            while task_date_from <= task_date_to:
                day_week: str = task_date_from.strftime("%A").lower()
                allowed_day: bool = task.scheduler.__dict__.get(day_week)
                if allowed_day:
                    if quantity:
                        required += task.quantity
                    else:
                        required += 1
                task_date_from += timedelta(days=1)
            task_needs_done['need'] = required
            tasks_needs_done.append(task_needs_done)
        return tasks_needs_done
