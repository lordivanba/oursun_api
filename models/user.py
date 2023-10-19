from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class User(BaseModel):
    id: Optional[str]
    isAuthorized : bool
    origin: int
    type: int
    username: str
    email: str
    user_password: str
    

class UserLoginSchema(BaseModel):
    email : EmailStr = Field(default = None)
    password : str = Field(default=None)