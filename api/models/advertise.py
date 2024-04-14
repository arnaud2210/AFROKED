from pydantic import BaseModel
from typing import Optional, Text
from datetime import datetime

class AdvertiseModel(BaseModel):
    full_name: str
    phone: str
    content: Text
    image: str

class AdvertiseData(BaseModel):
    id: str
    user_id: int
    full_name: str
    phone: str
    content: Text
    image: str
    created_at: Optional[datetime]