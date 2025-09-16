import pandas as pd
import datetime
from app.db.mongodb import get_collection
from app.services.huggingface_service import run_model

# 단일 텍스트 분석
def analyze_text(text: str):
    return run_model(text)

# CSV 분석
def analyze_csv(file_path: str):
    df = pd.read_csv(file_path)
    results = []

    for _, row in df.iterrows():
        text = str(row.get("text", ""))
        if not text.strip():
            continue
        analysis = run_model(text)
        results.append({**row.to_dict(), **analysis})

    output_path = file_path.replace(".csv", "_analyzed.csv")
    pd.DataFrame(results).to_csv(output_path, index=False)
    return output_path

# MongoDB 분석
async def analyze_mongo(limit: int = 1000):
    reviews_col = await get_collection("reviews")
    cursor = reviews_col.find({}, limit=limit)
    count = 0

    async for doc in cursor:
        text = doc.get("text", "")
        if not text.strip():
            continue
        analysis = run_model(text)

        await reviews_col.update_one(
            {"_id": doc["_id"]},
            {"$set": {"sentiment_analysis": analysis, "analyzed_at": datetime.datetime.utcnow()}}
        )
        count += 1
    return count
