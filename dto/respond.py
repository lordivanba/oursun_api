from pydantic import BaseModel
from typing import Optional

class Respond (BaseModel):
    success: bool
    data: Optional[dict]
    message: Optional[str]
