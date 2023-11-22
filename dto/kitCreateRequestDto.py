from fastapi import UploadFile
from pydantic import BaseModel
from typing import List, Optional


class KitCreateRequestDto(BaseModel):
    name : str
    description: str
    features: str
    price: float
    capacity: float
