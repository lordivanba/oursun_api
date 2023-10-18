from pydantic import BaseModel
from typing import Optional

class RespondUser (BaseModel):
    success: bool
    data: Optional[list]
    message: Optional[str]
