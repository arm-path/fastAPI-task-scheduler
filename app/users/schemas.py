from pydantic import BaseModel, EmailStr, Field, constr


class UserBaseSchema(BaseModel):
    username: str
    email: EmailStr


class RegistrationSchema(UserBaseSchema):
    username: constr(pattern=r'^[a-zA-Z0-9_]+$') = Field(max_length=32)
    password: str


class AuthenticationSchema(BaseModel):
    username: str
    password: str


class UserReadSchema(UserBaseSchema):
    id: int
    active: bool


class UserRecoveryPasswordSchema(BaseModel):
    email: EmailStr


class UserRecoveryPasswordEditSchema(BaseModel):
    password1: str
    password2: str

class JWTPyloadSchema(BaseModel):
    id: str
    exp: int