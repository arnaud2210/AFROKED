from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from models.product import ProductData, ProductDelete, ProductModel, ProductEdit
from models.botuser import BotUserModel
from routers.botuser import get_current_bot_user
from database.mongodb import connect_to_mongo
from utils.services.firebase import upload_file
from utils.utils import JWTBearer, check_product_storage, check_value
import starlette.status as status
from datetime import datetime
from pymongo import DESCENDING
from bson.objectid import ObjectId
from typing import Text, Optional, Dict


router = APIRouter()

@router.get("/{category_id}/products", response_model=list[ProductData])
async def get_all_products_by_category(
    category_id: str,
    user: BotUserModel = Depends(get_current_bot_user),
    db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):

    collection: AsyncIOMotorCollection = db["products"]

    query = {"category_id": category_id, "created_by": str(user.user_id)}

    products = await collection.find(query).sort("created_at", DESCENDING).to_list(length=None)

    formatted_products = [
        ProductData(
            id=str(ObjectId(product["_id"])),
            name=product["name"],
            price=product["price"],
            stock=product["stock"],
            description=product['description'],
            image=product["image"],
            category_id=product["category_id"],
            created_by=product["created_by"],
            visibility=product["visibility"],
            currency=product["currency"],
            created_at=product["created_at"],
            updated_at=product["updated_at"]
        )
        for product in products
    ]

    return formatted_products
