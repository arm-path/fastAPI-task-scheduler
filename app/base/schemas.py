from pydantic import BaseModel
from typing import Literal, Optional


class ResponseDetailSchema(BaseModel):
    code: Literal['success', 'warning', 'exception', 'fatal']
    data: Optional[dict]
    message: Optional[str]


class ResponseSchema(BaseModel):
    detail: ResponseDetailSchema