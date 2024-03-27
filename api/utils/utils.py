import os
import config
from jose import JWTError, jwt
from passlib.context import CryptContext
import time
from typing import Optional
import sys

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from ssl import create_default_context


from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from database.mongodb import connect_to_mongo

from bson.objectid import ObjectId
import starlette.status as status



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_env_var(key):
    return os.getenv(key, None)

def create_jwt_token(data: dict) -> str:
    data.update({"expires": time.time() + 84600})
    return jwt.encode(data, config.SECRET_KEY, algorithm="HS256")

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms="HS256")
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid


def read_html_template(file_name: str, data) -> str:
    # Lire le fichier HTML
    mail_path = os.path.dirname(__file__)
    
    if getattr(sys, 'frozen', False):
        mail_path = f"{sys._MEIPASS}/utils"
    
    with open(f"{mail_path}/{file_name}", "r", encoding="utf-8") as file:
        html_content= file.read().replace("{user_code}", str(data))
        file.close()

    return html_content

async def send_email(to_email: str, subject: str, body: str, body_type: str = "plain"):
    # Paramètres SMTP
    smtp_server = config.SMTP_SERVER
    smtp_port = config.SMTP_PORT
    smtp_username = config.SMTP_USERNAME
    smtp_password = config.SMTP_PASSWORD

    # Adresse e-mail expéditeur
    from_email = config.SMTP_FROM

    # Création du message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Ajout du corps du message
    msg.attach(MIMEText(body, body_type))

    # Connexion au serveur SMTP et envoi de l'e-mail
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi de l'e-mail : {str(e)}")

def check_value(value):
    if value <= 0:
        return False
    else:
        return True

async def check_product_storage(product_id, quantity: int, db: AsyncIOMotorDatabase = Depends(connect_to_mongo)):
    collection: AsyncIOMotorCollection = db["products"]

    product = await collection.find_one({"_id": ObjectId(product_id)})

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ce produit n'a pas été retrouvé")

    if quantity > product["stock"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La limite du stock est dépassée. Veuillez revoir votre quantité de commande.")
    
    if check_value(quantity) == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La quantité de votre commande ne peut-être nulle ou négative.")
    
    stock_update = product["stock"] - quantity

    await collection.update_one({"_id": ObjectId(product_id)}, {"$set": {"stock": stock_update}})

    return True
