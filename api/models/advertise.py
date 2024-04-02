from pydantic import BaseModel
from typing import Optional, Text
from datetime import datetime

class AdvertiseModel(BaseModel):
    content: Text

class AdvertiseData(BaseModel):
    id: str
    user_id: int
    content: Text
    created_at: Optional[datetime]