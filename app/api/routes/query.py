from fastapi import APIRouter
from app.db.mongodb import db
from datetime import datetime

router = APIRouter()

@router.post("/")
async def run_query(userId: str, query: str):
    # 나중에 AI 모델 붙이면 여기서 처리
    fake_answer = f"'{query}'에 대한 더미 답변입니다."
    result = {
        "userId": userId,
        "query": query,
        "output": {"answer": fake_answer},
        "createdAt": datetime.utcnow(),
    }
    await db.results.insert_one(result)
    return {"message": "쿼리 처리 완료", "answer": fake_answer}
