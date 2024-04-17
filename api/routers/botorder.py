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
from itertools import groupby

router = APIRouter()


@router.get("/all", response_model=list, dependencies=[Depends(JWTBearer())])
async def get_user_orders(user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["orders"]
    products : AsyncIOMotorCollection = db["products"]
    
    orders = await collection.find({"status": False}).to_list(length=None)

    items = []
    for order in orders:
        product_data = await products.find_one({"_id": ObjectId(order["product_id"]), "created_by": str(user.user_id)})

        order_items = {
            "product_id": str(ObjectId(product_data["_id"])),
            "product_name": product_data["name"],
            "product_image": product_data["image"],
            "quantity": order["quantity"],
            "unit_price": product_data["price"],
            "currency": product_data["currency"],
            "total_unit": order["quantity"] * product_data["price"],
            "user_id": order["user_id"]
        }

        items.append(order_items)
    
    items.sort(key=lambda x: x["user_id"])
    
    grouped_orders = []
    for user_id, group in groupby(items, key=lambda x: x["user_id"]):
        user_orders = list(group)
        total_order_amount = sum(order['total_unit'] for order in user_orders)
        user_data = {
            "user_id": user_id,
            "orders": user_orders,
            "total_order_amount": total_order_amount
        }
        grouped_orders.append(user_data)
    
    return grouped_orders


@router.put("/validate/{seller_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def validate_order(seller_id: int, user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["orders"]

    result = await collection.update_many(
        {"user_id": seller_id, "status": False},
        {
            "$set": {"status": True}
        }
    )

    if result.modified_count > 0:
        return {"detail": "Commande validée avec succès"}
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Echec de la mise à jour")

