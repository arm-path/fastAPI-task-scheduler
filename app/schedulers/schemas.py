from pydantic import BaseModel


class SchedulerBaseSchema(BaseModel):
    title: str
    monday: bool
    tuesday: bool
    wednesday: bool
    thursday: bool
    friday: bool
    saturday: bool
    sunday: bool


class SchedulerCreateUpdateSchema(SchedulerBaseSchema):
    pass


class SchedulerListSchema(SchedulerBaseSchema):
    id: int


class SchedulerDetailSchema(SchedulerBaseSchema):
    id: int
