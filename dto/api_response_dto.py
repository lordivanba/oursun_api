from typing import Optional
from pydantic import BaseModel

class ApiResponseDto (BaseModel):
    success: bool
    data: Optional[list]
    message: str

