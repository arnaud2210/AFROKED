from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_asyncio import AsyncIOMotorDatabase
import config


async def connect_to_mongo() -> AsyncIOMotorDatabase:
    #db_path = f"mongodb://{config.DB_PROD_LINK}:{config.DB_PORT}"
    db_path = f"{config.DB_PROD_LINK}"
    client = AsyncIOMotorClient(db_path)
    database = client[config.DB_NAME]
    return database