from pydantic import BaseModel
from typing import Optional

class DtoUser(BaseModel):
    id: str
    origin : int
    type: int
    username: str
    email: str