from pydantic import BaseModel
from typing import Optional


class ReviewCreateRequestDto(BaseModel):
    panels_number: int
    location: str
    payment_type: str
    previous_bill: float
    current_bill: float
    total_savings: float
