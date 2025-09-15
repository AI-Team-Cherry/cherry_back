from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.services.analytics_service import analyze_query
from app.services.analysis_result_generator import generate_analysis_result

router = APIRouter()

class AnalyticsIn(BaseModel):
    query: str

@router.post("/")
async def run_analytics(body: AnalyticsIn) -> Dict[str, Any]:
    # 1) 질의 분석 실행
    res = await analyze_query(body.query)

    # 2) 결과 생성
    analysis_result = generate_analysis_result(
        body.query,
        res["mongo"]["results"],
        res["rag"]
    )
    return {"status": "ok", "analysis": analysis_result}
