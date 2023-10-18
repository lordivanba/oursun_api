from pydantic import BaseModel
from typing import Optional

class RespondUpdateUserDto(BaseModel):
    success: bool
    message: str