from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.services.analytics_service import analyze_query
from app.services.analysis_result_generator import generate_analysis_result
from app.services.report_service import generate_report

router = APIRouter()

class IntegratedIn(BaseModel):
    query: str
    report_title: str

@router.post("/")
async def run_integrated(body: IntegratedIn) -> Dict[str, Any]:
    # 분석
    res = await analyze_query(body.query)
    analysis_result = generate_analysis_result(
        body.query,
        res["mongo"]["results"],
        res["rag"]
    )

    # 리포트 생성
    report = generate_report(body.report_title, analysis_result)

    # 통합 반환
    return {
        "status": "ok",
        "analysis": analysis_result,
        "report": report
    }
