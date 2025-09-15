from typing import Dict

def to_pipeline(query: str) -> Dict:
    # ✅ 실제 컬렉션명은 "product"
    target_collection = "product"

    if "브랜드별 매출" in query:
        return {
            "collection": target_collection,
            "pipeline": [
                {"$group": {"_id": "$brand", "total_sales": {"$sum": "$sales_cum"}}},
                {"$sort": {"total_sales": -1}},
                {"$limit": 10}
            ]
        }

    if "월별 매출" in query:
        return {
            "collection": "orders",
            "pipeline": [
                {"$group": {"_id": {"$substr": ["$order_date", 0, 7]},
                            "monthly_sales": {"$sum": "$total_amount"}}},
                {"$sort": {"_id": 1}}
            ]
        }

    if "고객 연령대" in query:
        return {
            "collection": "buyers",
            "pipeline": [
                {"$group": {"_id": "$age", "cnt": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
        }

    # 기본 fallback
    return {
        "collection": target_collection,
        "pipeline": [{"$limit": 5}]
    }
