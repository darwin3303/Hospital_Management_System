from pydantic import BaseModel, Field, ConfigDict
from app.core.schemas import ORMModel


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(ORMModel):
    id: str
    username: str
    role: str
    is_active: bool


class LoginResponseData(BaseModel):
    access_token: str
    user: UserOut


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)
    role: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=100)


class UserStatusUpdateRequest(BaseModel):
    is_active: bool