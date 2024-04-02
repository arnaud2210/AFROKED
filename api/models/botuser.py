from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BotUserModel(BaseModel):
    user_id: int
    plateform: str

class BotUserData(BaseModel):
    id: str
    user_id: int
    plateform: str
    joined_at: Optional[datetime]