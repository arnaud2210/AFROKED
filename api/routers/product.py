from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from models.product import ProductData, ProductDelete
from models.user import User
from routers.user import get_current_user
from database.mongodb import connect_to_mongo
from utils.utils import JWTBearer, check_value
from utils.services.firebase import upload_file
import starlette.status as status
from datetime import datetime
from pymongo import DESCENDING
from bson.objectid import ObjectId
from typing import Text, Optional, Dict
import os
import uuid

router = APIRouter()

FILE_PATH = "static/upload"

@router.post("/create", response_model=ProductData, dependencies=[Depends(JWTBearer())])
async def create_product(
    name: str = Form(...),
    description: Optional[Text] = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: str = Form(...),
    currency: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user), 
    db: AsyncIOMotorDatabase = Depends(connect_to_mongo)
    ):

    collection: AsyncIOMotorCollection = db["products"]

    if check_value(stock) == False or check_value(price) == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le prix ou la quantité doivent être non nulles et positives.")

    filename = f"{str(uuid.uuid4())}_{file.filename}"

    file_path = os.path.join(FILE_PATH, filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    product_data = {
        "name": name,
        "price": price,
        "stock": stock,
        "description": description,
        "image": upload_file(file_path),
        "category_id": category_id,
        "created_by": user.email,
        "visibility": False,
        "currency": currency,
        "created_at": datetime.now(),
        "updated_at": datetime.now() 
    }

    
    existing = await collection.find_one({"name": name})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ce produit existe déjà sous ce nom")
        
    result = await collection.insert_one(product_data)

    if result.inserted_id:
        return ProductData(
            id=str(result.inserted_id),
            name=name,
            price=product_data["price"],
            stock=product_data["stock"],
            description=description,
            image=product_data["image"],
            category_id=product_data["category_id"],
            created_by=user.email,
            visibility=product_data["visibility"],
            created_at=product_data["created_at"],
            updated_at=product_data["updated_at"]
        )

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erreur lors de l'enregistrement ")

@router.put("/edit", response_model=dict, dependencies=[Depends(JWTBearer())])
async def edit_product(
    product_id: str = Form(...),
    name: str = Form(...),
    description: Optional[Text] = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    category_id: str = Form(...),
    currency: str = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(connect_to_mongo)
    ):

    collection: AsyncIOMotorCollection = db["products"]

    existing = await collection.find_one({"_id": ObjectId(product_id), "created_by": user.email})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce produit n'existe pas")
    
    if check_value(stock) == False or check_value(price) == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le prix ou la quantité doivent être non nulles et positives.")

    filename = f"{str(uuid.uuid4())}_{file.filename}"

    file_path = os.path.join(FILE_PATH, filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    product_data = {
        "name": name,
        "price": price,
        "stock": stock,
        "description": description,
        "image": upload_file(file_path),
        "category_id": category_id,
        "currency": currency,
        "updated_at": datetime.now() 
    }
        
    result = await collection.update_one({"_id": ObjectId(product_id)}, {"$set": product_data})
    
    if result.matched_count > 0:
        return {"detail" : "Mis à jour avec succès"}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Une erreur s'est produite lors de la mise à jour.")

@router.get("/me/all", response_model=list[ProductData], dependencies=[Depends(JWTBearer())])
async def get_user_products(user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]
    users: AsyncIOMotorCollection = db["users"]

    user_admin = await users.find_one({"email": user.email, "roles.admin": True})

    if user_admin:
        products = await collection.find({}).sort("created_at", DESCENDING).to_list(length=None)
    else:
        products = await collection.find({"created_by": user.email}).sort("created_at", DESCENDING).to_list(length=None)

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

@router.get("/all", response_model=list[ProductData])
async def get_all_products(db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]

    products = await collection.find({"visibility": True}).sort("created_at", DESCENDING).to_list(length=None)

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

@router.get("/{product_id}", response_model=ProductData)
async def get_product_details(product_id: str, db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]

    query = {"_id": ObjectId(product_id)}

    product = await collection.find_one(query)
     
    formatted_product = ProductData(
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
        
    return formatted_product

@router.put("/validate/{product_id}", response_model=dict, dependencies=[Depends(JWTBearer())])
async def validate_product(product_id: str, user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]
    users: AsyncIOMotorCollection = db["users"]

    user_admin = await users.find_one({"email": user.email, "roles.admin": True})
    if not user_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    existing = await collection.find_one({"_id": ObjectId(product_id)})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce produit n'existe pas")
    
    await collection.update_one({"_id": ObjectId(product_id)}, {"$set": {"visibility": True}})

    return {"detail": "Produit mis à jour avec succès"}

@router.delete("/delete", response_model=dict, dependencies=[Depends(JWTBearer())])
async def remove_product(product: ProductDelete, user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]

    existing = await collection.find_one({"_id": ObjectId(product.id), "created_by": user.email})
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cette catégorie n'existe pas")
    
    await collection.delete_one({"_id": ObjectId(product.id)})
    
    return {"detail" : "Supprimé avec succès"}
