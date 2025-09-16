# app/services/sentiment_mongo.py
from app.db.mongodb import get_database
from app.services.sentiment_service import sentiment_service
from datetime import datetime

async def analyze_reviews_mongo(limit: int = 100):
    """
    MongoDB에서 리뷰 가져와 감정 분석 후 업데이트
    """
    db = await get_database()
    reviews = db["reviews"]

    cursor = reviews.find({"text": {"$exists": True}}).limit(limit)

    results = []
    async for review in cursor:
        text = review.get("text", "")
        if not text:
            continue

        analysis = sentiment_service.analyze_text(text)

        update_doc = {
            "overall_sentiment": analysis["overall_sentiment"],
            "overall_confidence": analysis["overall_confidence"],
            "analyzed_at": datetime.utcnow()
        }

        await reviews.update_one({"_id": review["_id"]}, {"$set": update_doc})
        results.append({**review, **update_doc})

    return results
