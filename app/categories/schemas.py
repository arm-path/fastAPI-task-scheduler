from pydantic import BaseModel


class CategoryBaseSchema(BaseModel):
    title: str


class CategoryCreateUpdateSchema(CategoryBaseSchema):
    title: str


class CategoryListSchema(CategoryCreateUpdateSchema):
    id: int
    title: str


class CategoryDetailSchema(CategoryListSchema):
    pass
