from pydantic import BaseModel
from typing import Optional

class RequestUpdateUserDto(BaseModel):
    username : str
    user_password: str
