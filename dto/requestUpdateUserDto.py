from pydantic import BaseModel
from typing import Optional

class RequestUpdateUserDto(BaseModel):
    username : str
    email : str
    user_password: str
