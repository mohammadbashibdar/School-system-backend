from pydantic import BaseModel, Field
from sqlmodel import asc, desc
from typing import Literal


class UserPublic(BaseModel):
    name: str
    mobile: str
    age: int | None
    is_enabled: bool | None = True


class UserInDB(UserPublic):
    hashed_password: str


class StudentPublic (BaseModel):
    name: str

class StudentInDB(StudentPublic):
    hashed_password: str

class EnrollmentPublic(BaseModel):
    presenting_id : int
    student_id : int

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Log(BaseModel):
    id : int
    user_id : int
    username : str | None

class SurveyCategory(BaseModel):
    id: int
    section_name: str | None

class Survey(BaseModel):
    username: str |None
    title: str
    description: str
    category_id: int

class FilterParams(BaseModel):
    page_number: int = Field(1, gt= 0)
    page_size: int = Field(5, gt=0, lt= 50)
    order_by: str | None = None
    order_type: Literal["asc", "desc"] = "asc"
    query: str | None = None