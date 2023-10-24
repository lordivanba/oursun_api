from pydantic import BaseModel
from typing import Optional


class KitCreateRequestDto(BaseModel):
    name: str
    description: str
    features: str
    price: float