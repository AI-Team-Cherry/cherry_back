from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, List
from app.viz.chart_generator import generate_chart

router = APIRouter()

class VizIn(BaseModel):
    query: str
    data: List[Dict[str, Any]]
    chart_type: str = "bar"

@router.post("/")
async def generate_viz(body: VizIn) -> Dict[str, Any]:
    chart = generate_chart(body.chart_type, body.query, body.data)
    return {"status": "ok", "chart": chart}
