from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from models.product import ProductData, ProductDelete, ProductModel, ProductEdit
from models.botuser import BotUserModel
from routers.botuser import get_current_bot_user
from database.mongodb import connect_to_mongo
from utils.utils import JWTBearer, check_product_storage, check_value
import starlette.status as status
from datetime import datetime
from pymongo import DESCENDING
from bson.objectid import ObjectId
from typing import Text, Optional, Dict
import re

router = APIRouter()

@router.post("/create", response_model=ProductData, dependencies=[Depends(JWTBearer())])
async def create_product(product: ProductModel, user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]

    product_data = product.dict()

    name = product_data["name"]
    price = product_data["price"]
    stock = product_data["stock"]
    description = product_data["description"]
    image = product_data["image"]
    category_id = product_data["category_id"]
    currency = product_data["currency"]
    visibility = False
    created_at = datetime.now()

    result = await collection.insert_one(
        {
            **product_data,
            "created_by": str(user.user_id),
            "visibility": visibility,
            "created_at": created_at,
            "updated_at": created_at
        }
    )

    if result.inserted_id:
        return ProductData(
            id=str(result.inserted_id),
            name=name,
            price=price,
            stock=stock,
            description=description,
            image=image,
            category_id=category_id,
            created_by=str(user.user_id),
            visibility=visibility,
            currency=currency,
            created_at=created_at,
            updated_at=created_at
        )
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de l'enregistrement")

@router.post("/search", response_model=list[ProductData])
async def search_product(search_term: str, user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]

    regex_pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    query = {"created_by": str(user.user_id), "name": {"$regex": regex_pattern}}

    products = await collection.find(query).sort("name", DESCENDING).to_list(length=None)
     
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

@router.get("/me/all", response_model=list[ProductData], dependencies=[Depends(JWTBearer())])
async def get_user_products(user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]
    
    products = await collection.find({"created_by": user.user_id}).sort("created_at", DESCENDING).to_list(length=None)

    formatted_user_products = [
        ProductData(
            id=str(ObjectId(product["_id"])),
            name=product["name"],
            price=product["price"],
            stock=product["stock"],
            description=product['description'],
            image=product["image"],
            category_id=product["category_id"],
            created_by=user.email,
            visibility=product["visibility"],
            currency=product["currency"],
            created_at=product["created_at"],
            updated_at=product["updated_at"]
        )
        for product in products
    ]
    
    return formatted_user_products

@router.put("/edit/{product_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def edit_product(product_id: str, product: ProductEdit, user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]

    existing = await collection.find_one({"_id": ObjectId(product_id), "created_by": user.email})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce produit n'existe pas")
    
    product_data = product.dict()
    updated_at = datetime.now()
    
    if check_value(product.stock) == False or check_value(product.price) == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le prix ou la quantité doivent être non nulles et positives.")
    
    result = await collection.update_one(
        {"_id": ObjectId(product_id)},
        {
            "$set": {
                **product_data,
                "updated_at": updated_at
            }
        }
    )

    if result.matched_count > 0:
        return {"detail" : "Mis à jour avec succès"}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Une erreur s'est produite lors de la mise à jour.")

@router.delete("/{product_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def remove_product(product_id: str, user: BotUserModel = Depends(get_current_bot_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]

    existing = await collection.find_one({"_id": ObjectId(product_id), "created_by": str(user.user_id)})
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produit non trouvé")
    
    await collection.delete_one({"_id": ObjectId(product_id)})
    
    return {"detail" : "Supprimé avec succès"}
