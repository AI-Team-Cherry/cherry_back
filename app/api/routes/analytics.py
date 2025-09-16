# app/api/routes/analytics.py
from fastapi import APIRouter, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.db.mongodb import db

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# =========================
# 1. KPI (총합 지표)
# =========================
@router.get("/kpis")
async def get_kpis() -> Dict[str, Any]:
    total_sales = await db.orders.aggregate([
        {"$group": {"_id": None, "sum": {"$sum": "$total_amount"}}}
    ]).to_list(1)
    orders = await db.orders.count_documents({})
    customers = await db.orders.distinct("buyer_id")
    return {
        "totalSales": total_sales[0]["sum"] if total_sales else 0,
        "orders": orders,
        "customers": len(customers),
        "dod": "+0%"   # TODO: 전일 대비 증감률 계산
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
