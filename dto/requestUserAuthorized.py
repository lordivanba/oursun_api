from pydantic import BaseModel
from typing import Optional

class RequestUserAuthorized(BaseModel):
    isAuthorized : bool