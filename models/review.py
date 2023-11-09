from pydantic import BaseModel
from typing import Optional


class Review(BaseModel):
    id: str
    panels_number: int
    location: str
    payment_type: str
    previous_bill: float
    current_bill: float
    total_savings: float
