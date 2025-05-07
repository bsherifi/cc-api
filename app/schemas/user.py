from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


class PlanBase(BaseModel):
    name: str
    rate_limit: int
    initial_credits: int


class PlanCreate(PlanBase):
    pass


class PlanInDB(PlanBase):
    id: int

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    plan_id: int


class UserLogin(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    api_key: str
    credits: int
    rate_limit: int


class UserInDB(UserBase):
    id: int
    credits: int
    api_key: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    plan: PlanInDB

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    id: int
    email: EmailStr
    credits: int
    api_key: str
    plan: PlanInDB

    class Config:
        from_attributes = True 