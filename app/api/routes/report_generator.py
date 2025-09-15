from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from app.services.report_service import generate_report
from app.services.analytics_service import analyze_query
from app.services.analysis_result_generator import generate_analysis_result

router = APIRouter()

class ReportIn(BaseModel):
    title: str
    query: str

@router.post("/")
async def generate(body: ReportIn) -> Dict[str, Any]:
    # 분석 실행
    res = await analyze_query(body.query)
    analysis_result = generate_analysis_result(
        body.query,
        res["mongo"]["results"],
        res["rag"]
    )

    # 리포트 생성
    report = generate_report(body.title, analysis_result)
    return {"status": "ok", "report": report}
