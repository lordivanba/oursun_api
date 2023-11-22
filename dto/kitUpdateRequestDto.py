from pydantic import BaseModel
from typing import Optional


class KitUpdateRequestDto(BaseModel):
    name : str
    description: str
    features: str
    price: float
    capacity: float