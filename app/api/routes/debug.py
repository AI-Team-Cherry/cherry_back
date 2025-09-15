from fastapi import APIRouter
from app.db.mongodb import db

router = APIRouter()

@router.get("/db-stats")
async def db_stats():
    collections = await db.list_collection_names()
    stats = {}
    for c in collections:
        count = await db[c].count_documents({})
        sample = await db[c].find_one() or {}
        stats[c] = {
            "count": count,
            "sample_keys": list(sample.keys())
        }
    return {"collections": collections, "stats": stats}
