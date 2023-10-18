from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[str]
    isAuthorized : bool
    origin: int
    type: int
    username: str
    email: str
    user_password: str