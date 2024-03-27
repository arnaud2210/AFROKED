from fastapi import APIRouter, Depends, HTTPException, Body
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from models.user import UserCreate, User, UserLogin, UserForgotPassword, UserResetPassword
from database.mongodb import connect_to_mongo
from utils.utils import create_jwt_token, get_env_var, get_password_hash, verify_password, JWTBearer, decodeJWT, read_html_template, send_email
import re
import starlette.status as status
from typing import Annotated, Union
from fastapi.security import HTTPBasic
from jose import JWTError, jwt
import secrets
from datetime import datetime, timedelta


router = APIRouter()

security = HTTPBasic()

async def get_current_user(token: str = Depends(create_jwt_token)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Veuillez vous reconnecter",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, get_env_var("SECRET_KEY"), algorithms=["HS256"])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return User(username=username)

async def generate_unique_code(tokens: AsyncIOMotorCollection, email) -> str:
    max_retries = 20
    retries = 0
    
    while retries < max_retries:
        # Génère un code à 6 chiffres
        code = secrets.randbelow(1000000)
        code_str = f"{code:06}"
        
        expiration_date = datetime.utcnow() + timedelta(minutes=5)


        # Vérifie s'il est unique dans la base de données
        existing_code = await tokens.find_one({"code": code_str})
        if not existing_code:
            # Enregistre le code dans la base de données avec la date d'expiration
            await tokens.insert_one({"code": code_str, "expiration_date": expiration_date, "email": email})

            # Crée un index TTL sur le champ "expiration_date" (expireAfterSeconds est le temps en secondes avant expiration)
            await tokens.create_index("expiration_date", expireAfterSeconds=0)

            return code_str
        
        retries = retries + 1
        
    return None

async def verify_unique_code(tokens: AsyncIOMotorCollection, email: str, code_str: str) -> bool:
    existing_code = await tokens.find_one({"code": code_str, "email": email})
    if not existing_code:
        return False
    return True
        
async def save_user(user_create: UserCreate, db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    users: AsyncIOMotorCollection = db["users"]
   
    user_data = user_create.dict()

    email = user_data["email"]
    username = user_data["username"]
    password = user_data["password"]
    full_name = user_data["full_name"]
    user_data["roles"]["admin"] = False
    user_data["roles"]["mercant"] = True
    disabled = False

    user_data["password"] = get_password_hash(password)
    user_data["created_at"] = datetime.now()
    user_data["disabled"] = disabled

    # try:
    user = await users.find_one({"$or": [
        {"username": username},
        {"email": email}
    ]})
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Le nom ou le mail est dèjà utilisé")
    
    result = await users.insert_one(user_data)
    if result.inserted_id:
        return User(
            full_name=full_name,
            username=username,
            email=email,
            disabled=disabled
        )
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Une erreur s'est produite.") 
    # except Exception as e:
    #     print(e)
    #     print(traceback.format_exc())
    #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Une erreur s'est produite mais ce n'est pas de votre faute.")

async def get_current_user(token: str = Depends(JWTBearer()), db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    users: AsyncIOMotorCollection = db["users"]

    data = decodeJWT(token)

    user = await users.find_one({"username": data["username"]})

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Veuillez vous reconnecter")
    
    return User(
        username=user["username"],
        email=user["email"],
        disabled=user["disabled"],
        full_name=user["full_name"]
    )

@router.post("/register", response_model=User)
async def create_user(user_create: UserCreate, db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    await save_user(user_create, db)
    return user_create

@router.post("/login", response_model=dict)
async def login_for_access_token(user_data: UserLogin, db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    users: AsyncIOMotorCollection = db["users"]

    username = user_data.username
    password = user_data.password

    token = None

    user = await users.find_one({"$or": [
            {"username": username},
            {"email": username}
        ]})

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nom d'utilisateur incorrect.")
    
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mot de passe incorrect") 

    if user["disabled"] == True:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Votre compte à été désactivé.")
        
    token = create_jwt_token({"username": user["username"]})

    return {
        "token": token,
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "disabled": user["disabled"]
    }

@router.post("/forgot-password", response_model=dict)
async def forgot_password(user_data: UserForgotPassword, db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    users: AsyncIOMotorCollection = db["users"]
    tokens: AsyncIOMotorCollection = db["tokens"]

    email_or_username = user_data.email

    user = await users.find_one({"$or": [
            {"username": email_or_username},
            {"email": email_or_username}
        ]})

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet utilisateur n'existe pas.")
    
    await tokens.delete_many({"email": user["email"]})
    unique_code = await generate_unique_code(tokens, user["email"])
    if unique_code is not None:
        html_template = read_html_template("code.html", unique_code)

        await send_email(user["email"], "Réinitialisation de mot de passe", html_template, "html")

        return {"message": "Code envoyé avec succès"}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Une erreur s'est produite.")

@router.post("/reset-password", response_model=dict)
async def reset_password(data: UserResetPassword, db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    users: AsyncIOMotorCollection = db["users"]
    tokens: AsyncIOMotorCollection = db["tokens"]
    
    code_document = await tokens.find_one({"code": data.code, "expiration_date": {"$gte": datetime.utcnow()}})
    if not code_document:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code invalide ou expiré.")

    # Vérifie si l'utilisateur existe
    user = await users.find_one({"email": code_document["email"]})
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cet utilisateur n'existe pas.")

    # Met à jour le mot de passe de l'utilisateur
    hashed_password = get_password_hash(data.password)
    await users.update_one({"email": user["email"]}, {"$set": {"password": hashed_password}})

    # Supprime le code utilisé de la collection des codes
    await tokens.delete_one({"_id": code_document["_id"]})

    return {"message": "Mot de passe réinitialisé avec succès."}


@router.get("/me", dependencies=[Depends(JWTBearer())])
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user