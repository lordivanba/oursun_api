from pydantic import BaseModel
from typing import Optional

class RespondUserAuthorized (BaseModel):
    success: bool
    message: str
