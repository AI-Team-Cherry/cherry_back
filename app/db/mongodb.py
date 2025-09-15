from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from pymongo import ReturnDocument
from app.core.config import MONGO_URI, DB_NAME

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

users_collection    = db["users"]
products_collection = db["products"]
reviews_collection  = db["reviews_ai_sentiment"]
images_collection   = db["images"]
results_collection  = db["results"]
buyers_collection = db["buyers"]

async def insert_result(doc: dict):
    doc.setdefault("createdAt", datetime.utcnow())
    await results_collection.insert_one(doc)
    return doc

async def run_aggregation(collection: str, pipeline: list):
    col = db[collection]
    cursor = col.aggregate(pipeline)
    return [doc async for doc in cursor]

async def update_user(employeeId: str, update_data: dict):
    update_data["updatedAt"] = datetime.utcnow()
    return await users_collection.find_one_and_update(
        {"employeeId": employeeId},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )

async def update_last_login(employeeId: str):
    return await users_collection.update_one(
        {"employeeId": employeeId},
        {"$set": {"lastLogin": datetime.utcnow(), "updatedAt": datetime.utcnow()}}
    )
