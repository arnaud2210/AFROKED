from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OrderModel(BaseModel):
    cart_id: str
    user_id: int
    status: bool
    created_at: datetime


