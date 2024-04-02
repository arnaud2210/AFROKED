from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CartModel(BaseModel):
    product_id: str
    quantity: int

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "quantity": self.quantity
        }

class CartData(BaseModel):
    id: str
    user_id: int
    orders: List[CartModel]
    visibility: bool
    created_at: Optional[datetime]

class CartDelete(BaseModel):
    id: str
