from typing import Optional, Text
from pydantic import BaseModel
from datetime import datetime

class ProductModel(BaseModel):
    name: str
    price: float
    stock: int
    description: Optional[Text]
    image: str
    category_id: str
    currency: str

class ProductData(BaseModel):
    id: str
    name: str
    price: float
    stock: int
    description: Optional[Text]
    image: str
    category_id: str
    created_by: str
    visibility: bool
    currency: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class ProductEdit(BaseModel):
    name: str
    price: str
    stock: int
    description: Optional[Text]
    category_id: str
    currency: str

class ProductDelete(BaseModel):
    id: str
