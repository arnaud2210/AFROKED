from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from models.cart import CartModel, CartData, CartDelete
from models.botuser import BotUserModel
from routers.botuser import get_current_bot_user
from database.mongodb import connect_to_mongo
from utils.utils import JWTBearer, check_product_storage, cancel_product
import starlette.status as status
from datetime import datetime
from pymongo import DESCENDING
from bson.objectid import ObjectId
from typing import List

router = APIRouter()

@router.post("/create", response_model=dict, dependencies=[Depends(JWTBearer())])
async def create_or_update_cart(orders: List[CartModel], user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["shopping_cart"]

    # Utiliser un dictionnaire pour stocker les quantités par product_id
    quantities_by_product_id = {}

    for order in orders:
        product_id = order.product_id
        quantity = order.quantity
        await check_product_storage(product_id, quantity, db)
        
        # Ajouter la quantité au dictionnaire par product_id
        if product_id in quantities_by_product_id:
            quantities_by_product_id[product_id] += quantity
        else:
            quantities_by_product_id[product_id] = quantity

    # Mettre à jour ou insérer le panier complet dans la base de données
    existing_cart = await collection.find_one({"user_id": user.user_id, "visibility": False})
    if existing_cart:
        for order in existing_cart["orders"]:
            # Mettre à jour les quantités des produits existants dans le panier
            if order["product_id"] in quantities_by_product_id:
                order["quantity"] += quantities_by_product_id[order["product_id"]]
                # Supprimer le product_id du dictionnaire pour éviter la duplication
                del quantities_by_product_id[order["product_id"]]

        # Ajouter les nouveaux produits restants dans le dictionnaire au panier
        for product_id, quantity in quantities_by_product_id.items():
            existing_cart["orders"].append({"product_id": product_id, "quantity": quantity})
        
        # Mettre à jour le panier dans la base de données
        await collection.update_one({"user_id": user.user_id, "visibility": False}, {"$set": existing_cart})
    else:
        # Construire le panier complet avec les nouvelles commandes
        cart_data = {
            "user_id": user.user_id,
            "visibility": False,
            "created_at": datetime.now(),
            "orders": [{"product_id": product_id, "quantity": quantity} for product_id, quantity in quantities_by_product_id.items()]
        }
        # Insérer le nouveau panier dans la base de données
        await collection.insert_one(cart_data)

    return {"detail": "Panier mis à jour avec succès"}


@router.get("/me", response_model=dict, dependencies=[Depends(JWTBearer())])
async def get_shopping_cart(user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["shopping_cart"]
    products: AsyncIOMotorCollection = db["products"]

    cart_data = await collection.find_one({"user_id": user.user_id, "visibility": False})
    if cart_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Panier non trouvé")

    orders = cart_data["orders"]
    
    receipt = []
    for order in orders:
        product_exist = await products.find_one({"_id": ObjectId(order["product_id"])})

        receipt_details = {
            "product_id": str(ObjectId(product_exist["_id"])),
            "product_name": product_exist["name"],
            "product_image": product_exist["image"],
            "product_stock": product_exist["stock"],
            "quantity": order["quantity"],
            "unit_price": product_exist["price"],
            "total_unit": order["quantity"] * product_exist["price"]
        }

        receipt.append(receipt_details)
    
    cart_id = str(ObjectId(cart_data["_id"]))
    total_price = sum([(detail["total_unit"]) for detail in receipt])
    
    if cart_data:
        return {"cart_id": cart_id, "data": receipt, "total_price": total_price, "total_items": len(receipt)}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Panier non trouvé")

@router.put("/validate/{cart_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def validate_shopping_cart(cart_id: str, user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["shopping_cart"]
    orders: AsyncIOMotorCollection = db["orders"]

    cart_data = await collection.find_one({"_id": ObjectId(cart_id),"user_id": user.user_id, "visibility": False})
    if cart_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Panier non trouvé")
    
    await collection.update_one(
        {"_id": ObjectId(cart_id), "user_id": user.user_id},
        {
            "$set": {"visibility": True}
        }
    )

    await orders.insert_one({"cart_id": cart_id, "user_id": user.user_id, "status": False, "created_at": datetime.now()})

    return {"detail": "Panier validé avec succès"}

@router.put("/{product_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def update_shopping_cart(order: CartModel, user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["shopping_cart"]
    products: AsyncIOMotorCollection = db["products"]

    product_exist = await products.find_one({"_id": ObjectId(order.product_id)})

    if not product_exist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Produit avec l'ID {order.product_id} non trouvé")
    
    checking = await check_product_storage(order.product_id, order.quantity)

    if checking == True:
        collection.update_one(
            {"user_id": user.user_id, "visibility": False, "orders.product_id": order.product_id},
            {
                "$set": {"orders.$.quantity": order.quantity}
            }
        )

        return {"detail": "Panier mis à jour avec succès"}
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Une erreur s'est produite lors de la mise à jour.")
    
@router.delete("/{product_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def remove_product_from_shopping_cart(product_id: str, user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["shopping_cart"]
    
    existing_cart = await collection.find_one({"user_id": user.user_id, "visibility": False})
    if not existing_cart:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce panier n'a pas été retrouvé")
    
    # Vérifiez d'abord si le produit existe dans le panier
    product_to_delete = next((order for order in existing_cart['orders'] if order['product_id'] == product_id), None)
    if not product_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Produit avec l'ID {product_id} non trouvé dans le panier de l'utilisateur")
    
    # Quantité du produit à supprimer
    quantity_to_delete = product_to_delete.get('quantity')

    stock_update = await cancel_product(product_id, quantity_to_delete, db)
        
    if stock_update == True:
        # Utilisez update_one() avec $pull pour retirer l'élément du tableau orders
        result = await collection.update_one(
            {"user_id": user.user_id, "visibility": False},
            {"$pull": {"orders": {"product_id": product_id}}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Impossible de supprimer le produit avec l'ID {product_id} du panier de l'utilisateur")
        
        return {"detail": f"Produit avec l'ID {product_id} supprimé du panier avec succès"}
    
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Une erreur s'est porduite lors de la suppression")
