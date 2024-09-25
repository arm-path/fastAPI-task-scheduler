from pydantic import BaseModel


class ReportBaseForTask(BaseModel):
    title: str
    is_done: int = 0
