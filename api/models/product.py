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
    created_by: str

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
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class ProductEdit(BaseModel):
    id: str
    name: str
    price: str
    stock: int
    description: Optional[Text]
    image: str
    category_id: str
    visibility: bool
    updated_at: Optional[datetime]

class ProductDelete(BaseModel):
    id: str
