from pydantic import BaseModel
from typing import Optional

class DtoUser(BaseModel):
    id: str
    username: str
    email: str