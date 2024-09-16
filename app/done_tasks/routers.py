from fastapi import APIRouter


router = APIRouter(
    prefix='/list-tasks',
    tags=['List Tasks']
)