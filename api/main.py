from fastapi import FastAPI, Depends, HTTPException, Request

from routers import user, botuser, category, product, order, cart, advertise, botproduct
from database.mongodb import connect_to_mongo
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from fastapi.responses import RedirectResponse
from utils.utils import get_env_var
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import config
import asyncio
import os
import sys



app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "vs"})
static_path = os.path.dirname(__file__) + "/static"
templates_path = os.path.dirname(__file__) + "/templates"

if getattr(sys, 'frozen', False):
    static_path = f"{sys._MEIPASS}/static"
    templates_path = f"{sys._MEIPASS}/templates"
    
app.mount("/static", StaticFiles(directory=static_path), name="ui")


templates = Jinja2Templates(directory=templates_path)
app.include_router(user.router, prefix="/api/auth", tags=["User"])
app.include_router(botuser.router, prefix="/api/bot", tags=["Bot user"])
app.include_router(botproduct.router, prefix="/api/bot/products", tags=["Bot product"])
app.include_router(advertise.router, prefix="/api/advertise", tags=["Advertise Request"])
app.include_router(category.router, prefix="/api/categories", tags=["Category Request"])
app.include_router(product.router, prefix="/api/products", tags=["Product Request"])
app.include_router(cart.router, prefix="/api/cart", tags=["Shopping Cart Request"])


origins = ["*"]
app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def my_first_get_api():
    return {"message":"Bienvenue sur AFROKED."}


if __name__ == "__main__":
    uvicorn.run("main:app", host=config.SERVER_HOST, port=int(config.API_PORT), reload=True)
