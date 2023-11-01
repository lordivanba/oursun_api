from pydantic import BaseModel
from typing import Optional

class RequestUserDto(BaseModel):
    origin : int
    type: int
    username : str
    user_password: str
