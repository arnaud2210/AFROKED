from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from models.advertise import AdvertiseModel, AdvertiseData
from models.botuser import BotUserModel
from models.user import User
from routers.botuser import get_current_bot_user
from routers.user import get_current_user
from database.mongodb import connect_to_mongo
from utils.utils import JWTBearer
import starlette.status as status
from datetime import datetime
from pymongo import DESCENDING
from bson.objectid import ObjectId

router = APIRouter()

@router.post("/create", response_model=AdvertiseData, dependencies=[Depends(JWTBearer())])
async def create_advertise(advertise: AdvertiseModel, user: BotUserModel = Depends(get_current_bot_user),db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["advertisements"]

    advertise_data = advertise.dict()

    full_name = advertise_data["full_name"]
    phone = advertise_data["phone"]
    content = advertise_data["content"]
    image = advertise_data["image"]
    created_at = datetime.now()
       
    result = await collection.insert_one(
        {
            **advertise_data,
            "user_id": user.user_id,
            "created_at": created_at
        }
    )

    if result.inserted_id:
        return AdvertiseData(
            id=str(result.inserted_id),
            user_id=user.user_id,
            full_name=full_name,
            phone=phone,
            content=content,
            image=image,
            created_at=created_at
        )

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de l'enregistrement")

@router.get("/all", response_model=list[AdvertiseData], dependencies=[Depends(JWTBearer())])
async def get_all_advertisements(user: User = Depends(get_current_user), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["advertisements"]
    users: AsyncIOMotorCollection = db["users"]

    user_admin = await users.find_one({"email": user.email, "roles.admin": True})
    if not user_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
    advertisements = await collection.find({}).sort("created_at", DESCENDING).to_list(length=None)
    
    formatted_advertises = [
        AdvertiseData(
            id=str(ObjectId(advertise["_id"])),
            user_id=advertise["user_id"],
            full_name=advertise["full_name"],
            phone=advertise["phone"],
            content=advertise["content"],
            image=advertise["image"],
            created_at=advertise["created_at"]
        )
        for advertise in advertisements
    ]
    
    return formatted_advertises
    
    

    

