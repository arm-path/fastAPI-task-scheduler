from fastapi import FastAPI

from app.mail import router as mail_router
from app.users import router as user_router

app = FastAPI()

app.include_router(user_router)
app.include_router(mail_router)
