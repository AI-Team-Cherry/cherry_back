from fastapi import APIRouter, Query
from typing import Optional, List, Dict, Any
from app.db.mongodb import results_collection

router = APIRouter()

@router.get("/list")
async def list_results(userId: str, limit: int = 20):
    cursor = results_collection.find({"userId": userId}).sort("createdAt", -1).limit(limit)
    data: List[Dict[str, Any]] = [doc async for doc in cursor]
    # ObjectId 등 직렬화는 프런트에서 필요 시 처리 or 여기서 str 변환
    for d in data:
        if "_id" in d:
            d["_id"] = str(d["_id"])
    return {"status":"ok", "count": len(data), "items": data}
