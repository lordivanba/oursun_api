from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class ResponseQuotationsDto(BaseModel):
    id: str
    created_at: str
    kit_id: str
    kit_name: Optional[str]
    kit_price: Optional[float]
    user_id: str
    username: Optional[str]
