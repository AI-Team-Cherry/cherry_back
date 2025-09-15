# 리뷰 피처 처리 (간단 더미: 감성/카테고리 추정)
# TODO: KcELECTRA 등 실제 모델로 교체
async def analyze_review(content: str):
    sentiment = "positive" if any(k in content for k in ["좋", "만족", "추천"]) else "neutral"
    score = 0.85 if sentiment == "positive" else 0.5
    return {"sentiment": sentiment, "sentiment_score": score, "length": len(content)}
