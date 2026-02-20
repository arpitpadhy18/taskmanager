from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    role: str = Field(default="user")

    class Config:
        json_schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "jdoe@example.com",
                "password": "strongpassword123",
                "role": "user"
            }
        }

class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jdoe@example.com",
                "password": "strongpassword123",
            }
        }

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponseSchema(BaseModel):
    id: str
    fullname: str
    email: EmailStr
    created_at: datetime

class TaskSchema(BaseModel):
    title: str = Field(...)
    description: str = Field(...)
    assigned_to: str = Field(...)  # user_id
    due_date: str = Field(...)  # ISO date string
    status: str = Field(default="pending")  # pending, in_progress, completed
    priority: str = Field(default="medium")  # low, medium, high, urgent

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Design Landing Page",
                "description": "Create a responsive landing page design",
                "assigned_to": "user_id_here",
                "due_date": "2026-02-15",
                "status": "pending",
                "priority": "medium"
            }
        }

class TaskUpdateSchema(BaseModel):
    status: str = Field(...)
