from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from pymongo import ReturnDocument

# MongoDB 연결 URI
MONGO_URI = "mongodb+srv://cherry:1234@panguin5225.m6oav.mongodb.net/?retryWrites=true&w=majority&appName=Panguin5225"

# 전역 client
client = AsyncIOMotorClient(MONGO_URI)
db = client["musinsa_db"]

# collections
users_collection = db["users"]        # 사용자 계정
products_collection = db["product"]   # 상품
reviews_collection = db["reviews"]    # 리뷰
images_collection = db["images"]      # 이미지
results_collection = db["results"]    # 분석 결과

# 유틸 함수 (예시)
async def get_user(employeeId: str):
    return await users_collection.find_one({"employeeId": employeeId})

async def create_user(user_data: dict):
    user_data["createdAt"] = datetime.utcnow()
    user_data["updatedAt"] = datetime.utcnow()
    await users_collection.insert_one(user_data)
    return user_data

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
