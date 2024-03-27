from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from models.botuser import BotUserModel
from database.mongodb import connect_to_mongo
from utils.utils import create_jwt_token, get_env_var, JWTBearer, decodeJWT
from datetime import datetime
from jose import JWTError, jwt
import starlette.status as status


router = APIRouter()

async def get_current_bot_user(token: str = Depends(create_jwt_token)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Veuillez vous reconnecter",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, get_env_var("SECRET_KEY"), algorithms=["HS256"])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return BotUserModel(user_id=user_id)

async def get_current_bot_user(token: str = Depends(JWTBearer()), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    users: AsyncIOMotorCollection = db["botusers"]

    data = decodeJWT(token)

    botuser = await users.find_one({"user_id": data["user_id"]})

    if not botuser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Veuillez vous reconnecter")
    
    return BotUserModel(
        user_id=botuser["user_id"],
        plateform=botuser["plateform"]
    )

async def save_botuser(botuser: BotUserModel, db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["botusers"]

    user_data = botuser.dict()

    user_id = user_data["user_id"]
    joined_at = datetime.now()

    #user_exist = await collection.find_one({"user_id": user_id}, {"_id":0})

    token = create_jwt_token({"user_id": user_id})
        
    result = await collection.insert_one({**user_data, "joined_at": joined_at})

    if result.inserted_id:
        return {
            "token": token,
            "user_id": user_id
        }

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erreur lors de l'enregistrement ")

@router.post("/login", response_model=dict)
async def login_botuser(botuser: BotUserModel, db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["botusers"]

    user_exist = await collection.find_one({"user_id": botuser.user_id}, {"_id":0})

    token = create_jwt_token({"user_id": botuser.user_id})

    if user_exist is None:
        return await save_botuser(botuser, db)
    else:
        return {
            "token": token,
            "user_id": botuser.user_id
        }