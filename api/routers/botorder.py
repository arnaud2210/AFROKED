from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from models.order import OrderModel
from models.botuser import BotUserModel
from routers.botuser import get_current_bot_user
from database.mongodb import connect_to_mongo
from utils.utils import JWTBearer, check_product_storage
import starlette.status as status
from datetime import datetime
from pymongo import DESCENDING
from bson.objectid import ObjectId

router = APIRouter()


@router.get("/me/all", response_model=list, dependencies=[Depends(JWTBearer())])
async def get_user_orders(user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["orders"]
