from typing import Dict, List, Any
import datetime
import re

# ====== 헬퍼: 정규식 매칭 ======
def match_in_query(pattern: str, query: str) -> bool:
    return re.search(pattern, query) is not None


# ====== RULES ======
SORT_RULES = {
    r"잘\s*팔린": {"$sort": {"sales_cum": -1}},
    r"판매량\s*높": {"$sort": {"sales_cum": -1}},
    r"판매량\s*낮": {"$sort": {"sales_cum": 1}},
    r"인기": {"$sort": {"views_1m": -1}},
    r"조회수\s*많": {"$sort": {"views_1m": -1}},
    r"조회수\s*적": {"$sort": {"views_1m": 1}},
    r"평점\s*높": {"$sort": {"rating_avg": -1}},
    r"평점\s*낮": {"$sort": {"rating_avg": 1}},
    r"리뷰\s*좋": {"$sort": {"rating_avg": -1}},
    r"별점\s*높": {"$sort": {"rating_avg": -1}},
    r"비싼": {"$sort": {"price": -1}},
    r"싼": {"$sort": {"price": 1}},
    r"가격\s*높": {"$sort": {"price": -1}},
    r"가격\s*낮": {"$sort": {"price": 1}},
    r"(최근|최신)": {"$sort": {"createdAt": -1}},
    r"오래된": {"$sort": {"createdAt": 1}},
}

MATCH_RULES = {
    r"남자": {"gender": "M"},
    r"여자": {"gender": "F"},
    r"유니섹스": {"gender": "UNISEX"},
    r"상의": {"category_l1": {"$regex": "상의"}},
    r"하의": {"category_l1": {"$regex": "하의"}},
    r"신발": {"category_l1": {"$regex": "신발"}},
    r"가방": {"category_l1": {"$regex": "가방"}},
    r"액세서리": {"category_l1": {"$regex": "액세서리"}},
}

LIMIT_RULES = {
    r"(상위\s*10|10개)": {"$limit": 10},
    r"(상위\s*5|5개)": {"$limit": 5},
    r"(상위\s*3|3개)": {"$limit": 3},
}

AGG_RULES = {
    r"평균\s*가격": {"$group": {"_id": None, "avg_price": {"$avg": "$price"}}},
    r"평균\s*평점": {"$group": {"_id": None, "avg_rating": {"$avg": "$rating_avg"}}},
    r"총\s*판매량": {"$group": {"_id": None, "total_sales": {"$sum": "$sales_cum"}}},
    r"총\s*리뷰": {"$group": {"_id": None, "total_reviews": {"$sum": "$reviews_count"}}},
    r"최고가": {"$group": {"_id": None, "max_price": {"$max": "$price"}}},
    r"최저가": {"$group": {"_id": None, "min_price": {"$min": "$price"}}},
}

DATE_RULES = {
    r"오늘": {
        "createdAt": {
            "$gte": datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        }
    },
    r"이번주": {"createdAt": {"$gte": datetime.datetime.now() - datetime.timedelta(days=7)}},
    r"이번달": {"createdAt": {"$gte": datetime.datetime.now().replace(day=1)}},
    r"올해": {"createdAt": {"$gte": datetime.datetime(datetime.datetime.now().year, 1, 1)}},
}


# ====== PIPELINE BUILDER ======
def to_pipeline(query: str) -> Dict[str, Any]:
    target_collection = "product"

    # 특수 케이스
    if "브랜드별 매출" in query:
        return {
            "collection": target_collection,
            "pipeline": [
                {"$group": {"_id": "$brand", "total_sales": {"$sum": "$sales_cum"}}},
                {"$sort": {"total_sales": -1}},
                {"$limit": 10},
            ],
        }

    if "월별 매출" in query:
        return {
            "collection": "orders",
            "pipeline": [
                {
                    "$group": {
                        "_id": {"$substr": ["$order_date", 0, 7]},
                        "monthly_sales": {"$sum": "$total_amount"},
                    }
                },
                {"$sort": {"_id": 1}},
            ],
        }

    if "고객 연령대" in query:
        return {
            "collection": "buyers",
            "pipeline": [
                {"$group": {"_id": "$age", "cnt": {"$sum": 1}}},
                {"$sort": {"_id": 1}},
            ],
        }

    # 룰 기반
    pipeline: List[Dict[str, Any]] = []

    for rules in [MATCH_RULES, DATE_RULES, SORT_RULES, LIMIT_RULES, AGG_RULES]:
        for pattern, clause in rules.items():
            if match_in_query(pattern, query):
                # $match 여러 개 붙으면 누적됨
                if "$match" in clause:
                    pipeline.append({"$match": clause})
                else:
                    pipeline.append(clause)

    if not pipeline:
        pipeline = [{"$limit": 5}]

    return {"collection": target_collection, "pipeline": pipeline}
