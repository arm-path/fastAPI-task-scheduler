from datetime import date, timedelta

from sqlalchemy import Select, select, Result, func
from sqlalchemy.ext.asyncio import AsyncSession

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
        pass
