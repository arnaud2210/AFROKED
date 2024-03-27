from typing import Optional, Text
from pydantic import BaseModel
from datetime import datetime

class CategoryModel(BaseModel):
    name: str
    description: Optional[Text]

class CategoryData(BaseModel):
    id: str
    name: str
    description: Optional[Text]
    created_by: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class CategoryEdit(BaseModel):
    id: str
    name: str
    description: Optional[Text]

class CategoryDelete(BaseModel):
    id: str