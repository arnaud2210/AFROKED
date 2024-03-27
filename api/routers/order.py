"""from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from models.order import OrderModel, OrderData, OrderDelete
from models.cart import CartModel
from models.botuser import BotUserModel
from routers.botuser import get_current_bot_user
from database.mongodb import connect_to_mongo
from utils.utils import JWTBearer, check_product_storage, create_shopping_cart, check_order, add_new_order
import starlette.status as status
from datetime import datetime
from pymongo import DESCENDING
from bson.objectid import ObjectId

router = APIRouter()

@router.post("/create", response_model=OrderData, dependencies=[Depends(JWTBearer())])
async def create_order(order: OrderModel, user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["orders"]
    shopping_cart: AsyncIOMotorCollection = db["shopping_cart"]


    order_data = order.dict()

    product_id = order_data["product_id"]
    quantity = order_data["quantity"]
    ordered = False

    created_at = datetime.now()
    
    storage = await check_product_storage(product_id, quantity, db)
    
    if storage == True:

        result = await collection.insert_one(
            {
                "user_id": user.user_id,
                **order_data,
                "ordered": ordered,
                "created_at": created_at
            }
        )

        if result.inserted_id:

            order_id = str(result.inserted_id)
            cart_exist = await shopping_cart.find_one({"user_id": user.user_id, "order_id": order_id})
            
            if cart_exist is None:                
                user_cart = await create_shopping_cart(user.user_id, order_id, db)
                print("user_cart: ", user_cart)
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Une erreur s'est produite lors de la création du panier.")

            return OrderData(
                id=str(result.inserted_id),
                user_id=user.user_id,
                product_id=product_id,
                quantity=quantity,
                ordered=ordered,
                created_at=created_at
            )

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de l'enregistrement ")


@router.get("/me/all", response_model=list[OrderData], dependencies=[Depends(JWTBearer())])
async def get_user_orders(user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["orders"]

    user_orders = await collection.find({"user_id": user.user_id}).sort("created_at", DESCENDING).to_list(length=None)

    formatted_user_orders = [
        OrderData(
            id=str(ObjectId(order["_id"])),
            user_id=order["user_id"],
            product_id=order["product_id"],
            quantity=order["quantity"],
            ordered=order["ordered"],
            created_at=order["created_at"]
        )
        for order in user_orders
    ]
    
    return formatted_user_orders


@router.delete("/delete", response_model=dict, dependencies=[Depends(JWTBearer())])
async def remove_order(order: OrderDelete, user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["orders"]

    existing = await collection.find_one({"_id": ObjectId(order.id), "user_id": user.user_id})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cette commande n'existe pas")
    
    await collection.delete_one({"_id": ObjectId(order.id)})
    
    return {"detail" : "Supprimé avec succès"}
"""