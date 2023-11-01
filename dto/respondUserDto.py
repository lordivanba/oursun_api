from pydantic import BaseModel
from typing import Optional

class DtoUser(BaseModel):
    id: str
    isAuthorized : bool
    origin : int
    type: int
    username: str