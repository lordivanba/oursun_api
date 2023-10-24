from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Kit(BaseModel):
    id: Optional[str]
    name: str
    price: float
    description: str
    features: str
    images: list
