from datetime import date, timedelta

from sqlalchemy import Select, select, Result, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database.services import DatabaseService
from app.done_tasks import DoneTasks
from app.exceptions import ParamDatesMustBeDefinedException
from app.tasks import Tasks
from app.users.schemas import UserReadSchema


class ReportServices(DatabaseService):
    model = DoneTasks

    @classmethod
    async def base_report(cls, session: AsyncSession, user: UserReadSchema, date_from, date_to):
        if (date_from and not date_to) or (not date_from and date_to):
            raise ParamDatesMustBeDefinedException
        if not date_from and not date_to:
            today = date.today()
            date_from = today.replace(day=1)
            if today.month == 12:
                date_to = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                date_to = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        query_tasks: Select = (
            select(Tasks.title, func.count(DoneTasks.id))
            .join(DoneTasks, Tasks.id == DoneTasks.task_id)
            .where(
                Tasks.user_id == user.id,
                DoneTasks.is_done == True,
                DoneTasks.date > date_from,
                DoneTasks.date < date_to
            )
            .group_by(Tasks.title)
        )

        """
            SELECT tasks.title, COUNT(*) FROM done_tasks
            JOIN tasks
            ON tasks.id = done_tasks.task_id
            WHERE tasks.user_id=7 AND done_tasks.date > '2024-09-21' AND done_tasks.date < '2024-09-30'
            GROUP BY tasks.title
        """

        result_tasks: Result[tuple[Tasks]] = await session.execute(query_tasks)
        db_tasks = result_tasks.all()
        tasks = {}
        for title, count in db_tasks:
            tasks[title] = count
        return tasks

    @classmethod
    async def percentage_tasks_completed(cls, session: AsyncSession, user: UserReadSchema):
        today = date.today()
        date_from = today.replace(day=1)
        if today.month == 12:
            date_to = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            date_to = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        query: Select = (
            select(Tasks)
            .where(and_(Tasks.user_id == user.id,
                        or_(and_(Tasks.start_date >= date_from, Tasks.start_date <= date_to),
                            and_(Tasks.start_date <= date_from, Tasks.end_date > date_from))))
            .options(joinedload(Tasks.scheduler))
        )
        query_result: Result[tuple[Tasks]] = await session.execute(query)
        task_db = query_result.scalars().all()

        tasks_needs_done = []
        for task in task_db:
            task_needs_done = {'title': task.title}
            required_days = 0
            task_date_from = max(task.start_date, date_from)
            task_date_to = min(task.end_date, date_to)
            while task_date_from <= task_date_to:
                day_week: str = task_date_from.strftime("%A").lower()
                allowed_day: bool = task.scheduler.__dict__.get(day_week)
                if allowed_day:
                    required_days += 1
                task_date_from += timedelta(days=1)
            task_needs_done['needs_done'] = required_days
            tasks_needs_done.append(task_needs_done)

        tasks_done = await cls.base_report(session, user, None, None)
        results = []
        for task_need_done in tasks_needs_done:
            task = task_need_done.copy()
            task['done'] = 0
            for title, key in tasks_done.items():
                if task_need_done.get('title') == title:
                    task['done'] = key
            task['percent_done'] = round(task['done'] / task['needs_done'] * 100, 2)
            results.append(task)

        return results
