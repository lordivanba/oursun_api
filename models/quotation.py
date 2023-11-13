from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class Quotation(BaseModel):
    id: str
    created_at: str
    kit_id: str
    name_kit: str
    user_id: str
    username: str