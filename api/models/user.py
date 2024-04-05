from pydantic import BaseModel, EmailStr
from typing import Optional, Dict

class Role(BaseModel):
    admin: bool
    mercant: bool

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    roles: Role

    class Config:
        json_schema_extra = {
            "example": {
                "username": "string",
                "email": "user@example.com",
                "full_name": "string",
                "password": "string",
                "roles": {
                    "admin": False,
                    "mercant": False
                }
            }
        }

class UserForgotPassword(BaseModel):
    email: EmailStr
        
class UserResetPassword(BaseModel):
    code: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "arnaud",
                "password": "string"
            }
        }

class User(BaseModel):
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    username: str
    email: str
    roles: Role

class Token(BaseModel):
    access_token: str
    token_type: str