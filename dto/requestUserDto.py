from pydantic import BaseModel
from typing import Optional

class RequestUserDto(BaseModel):
    origin : int
    type: int
    username : str
    email : str
    user_password: str
