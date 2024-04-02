from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from models.category import CategoryModel, CategoryData, CategoryDelete, CategoryEdit
from models.product import ProductData
from models.user import User
from routers.user import get_current_user
from database.mongodb import connect_to_mongo
from utils.utils import JWTBearer
import starlette.status as status
from datetime import datetime
from pymongo import DESCENDING
from bson.objectid import ObjectId
from typing import Optional

router = APIRouter()

@router.post("/create", response_model=CategoryData, dependencies=[Depends(JWTBearer())])
async def create_category(category: CategoryModel, user: User = Depends(get_current_user),db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["categories"]

    category_data = category.dict()

    name = category_data["name"]
    description = category_data["description"]
    created_at = datetime.now()
    
    existing = await collection.find_one({"name": name})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cette categorie existe déjà")
        
    result = await collection.insert_one(
        {
            **category_data,
            "created_by": user.email,
            "created_at": created_at,
            "updated_at": created_at
        }
    )

    if result.inserted_id:
        return CategoryData(
            id=str(result.inserted_id),
            name=name,
            description=description,
            created_by=user.email,
            created_at=created_at,
            updated_at=created_at
        )

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de l'enregistrement")

@router.put("/edit", response_model=dict, dependencies=[Depends(JWTBearer())])
async def edit_category(category: CategoryEdit, user: User = Depends(get_current_user),db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["categories"]

    existing = await collection.find_one({"_id": ObjectId(category.id), "created_by": user.email})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cette catégorie n'existe pas")

    category_data = category.dict()
    updated_at = datetime.now()
        
    result = await collection.update_one(
        {"_id": ObjectId(category.id)},
        {
            "$set": {
                **category_data,
                "updated_at": updated_at
            }
        }
    )

    if result.matched_count > 0:
        return {"detail" : "Mis à jour avec succès"}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Une erreur s'est produite lors de la mise à jour.")

@router.get("/me/all", response_model=list[CategoryData], dependencies=[Depends(JWTBearer())])
async def get_user_categories(user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["categories"]

    user_categories = await collection.find({"created_by": user.email}).sort("created_at", DESCENDING).to_list(length=None)

    formatted_user_categories = [
        CategoryData(
            id=str(ObjectId(category["_id"])),
            name=category["name"],
            description=category["description"],
            created_by=category["created_by"],
            created_at=category["created_at"],
            updated_at=category["updated_at"]
        )
        for category in user_categories
    ]
    
    return formatted_user_categories

@router.get("/all", response_model=list[CategoryData])
async def get_user_categories(db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["categories"]

    categories = await collection.find({}).sort("created_at", DESCENDING).to_list(length=None)

    formatted_categories = [
        CategoryData(
            id=str(ObjectId(category["_id"])),
            name=category["name"],
            description=category["description"],
            created_by=category["created_by"],
            created_at=category["created_at"],
            updated_at=category["updated_at"]
        )
        for category in categories
    ]
    
    return formatted_categories

@router.get("/{category_id}/products", response_model=list[ProductData])
async def get_all_products_by_category(
    category_id: str,
    db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):

    collection: AsyncIOMotorCollection = db["products"]

    query = {"category_id": category_id, "visibility": True}

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

@router.delete("/delete", response_model=dict, dependencies=[Depends(JWTBearer())])
async def remove_category(category: CategoryDelete, user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["categories"]

    existing = await collection.find_one({"_id": ObjectId(category.id), "created_by": user.email})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cette catégorie n'existe pas")
    
    await collection.delete_one({"_id": ObjectId(category.id)})
    
    return {"detail" : "Supprimé avec succès"}
