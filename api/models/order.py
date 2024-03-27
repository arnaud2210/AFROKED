from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class OrderModel(BaseModel):
    product_id: str
    quantity: int

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "quantity": self.quantity
        }

class OrderData(BaseModel):
    id: str
    user_id: int
    orders: List[OrderModel]
    created_at: Optional[datetime]

class OrderDelete(BaseModel):
    id: str
