from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.analytics_service import analyze_query
from app.services.analysis_result_generator import generate_analysis_result
from datetime import datetime, timedelta
from app.db.mongodb import db 

router = APIRouter()

class AnalyticsIn(BaseModel):
    query: str

from fastapi import APIRouter, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.db.mongodb import db

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# =========================
# 1. KPI
# =========================
@router.get("/kpis")
async def get_kpis() -> Dict[str, Any]:
    # 총 매출
    total_sales = await db.orders.aggregate([
        {"$group": {"_id": None, "sum": {"$sum": "$total_amount"}}}
    ]).to_list(1)

    # 총 주문 수
    orders = await db.orders.count_documents({})

    # 총 고객 수 (buyer_id 고유값 개수)
    customers = await db.orders.distinct("buyer_id")
    customer_count = len(customers)

    # TODO: 전일 대비 증감률 (여기선 임시 값)
    dod = "+0%"

    return {
        "totalSales": total_sales[0]["sum"] if total_sales else 0,
        "orders": orders,
        "customers": customer_count,
        "dod": dod
    }


# =========================
# 2. 브랜드별 매출
# =========================
@router.get("/sales-by-dept")
async def sales_by_brand(
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = None
) -> List[Dict[str, Any]]:
    match = {}
    if from_ or to:
        match["order_date"] = {}
        if from_:
            match["order_date"]["$gte"] = from_
        if to:
            match["order_date"]["$lte"] = to

    pipeline = []
    if match:
        pipeline.append({"$match": match})

    pipeline.extend([
        {"$group": {"_id": "$brand_name", "sales": {"$sum": "$total_amount"}}},
        {"$project": {"_id": 0, "department": "$_id", "sales": 1}},
        {"$sort": {"sales": -1}}
    ])

    docs = await db.orders.aggregate(pipeline).to_list(None)
    return docs


# =========================
# 3. 매출 추이 (일자별 합계)
# =========================
@router.get("/timeseries")
async def timeseries(
    metric: str = "sales",
    from_: Optional[str] = Query(None, alias="from"),
    to: Optional[str] = None
) -> List[Dict[str, Any]]:
    match = {}
    if from_ or to:
        match["order_date"] = {}
        if from_:
            match["order_date"]["$gte"] = from_
        if to:
            match["order_date"]["$lte"] = to

    pipeline = []
    if match:
        pipeline.append({"$match": match})

    if metric == "sales":
        pipeline.extend([
            {"$group": {"_id": "$order_date", "value": {"$sum": "$total_amount"}}},
            {"$project": {"_id": 0, "date": "$_id", "value": 1}},
            {"$sort": {"date": 1}}
        ])
    elif metric == "orders":
        pipeline.extend([
            {"$group": {"_id": "$order_date", "value": {"$sum": 1}}},
            {"$project": {"_id": 0, "date": "$_id", "value": 1}},
            {"$sort": {"date": 1}}
        ])

    docs = await db.orders.aggregate(pipeline).to_list(None)
    return docs