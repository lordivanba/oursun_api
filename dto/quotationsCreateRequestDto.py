from pydantic import BaseModel
from typing import Optional

class QuotationsCreateRequestDto(BaseModel):
    kit_id: str
    user_id: str
    latitude: float
    longitude: float
    