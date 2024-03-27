from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CartModel(BaseModel):
    user_id: int
    order_id: str
    #ordered: bool

class CartData(BaseModel):
    id: str
    user_id: int
    order_id: str
    ordered: bool
    created_at: Optional[datetime]

class CartDelete(BaseModel):
    id: str