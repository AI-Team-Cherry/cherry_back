from fastapi import APIRouter
from app.db.mongodb import db

router = APIRouter()

@router.get("/{userId}")
async def get_results(userId: str):
    results = await db.results.find({"userId": userId}).to_list(100)
    for r in results:
        r["_id"] = str(r["_id"])
    return {"results": results}
