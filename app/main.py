from fastapi import FastAPI
from fastapi_pagination import add_pagination

from app.mail import router as mail_router
from app.users import router as user_router
from app.categories import router as category_router
from app.schedulers import router as scheduler_router
from app.tasks import router as task_router
from app.done_tasks import router as done_tasks_router

app = FastAPI()

app.include_router(user_router)
app.include_router(category_router)
app.include_router(scheduler_router)
app.include_router(task_router)
app.include_router(done_tasks_router)
app.include_router(mail_router)

add_pagination(app)
