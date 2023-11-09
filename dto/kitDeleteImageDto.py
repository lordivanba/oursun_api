from fastapi import UploadFile
from pydantic import BaseModel
from typing import List, Optional

class KitDeleteImageDto(BaseModel):
    id: str
    image_url: str