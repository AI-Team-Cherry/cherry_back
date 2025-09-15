from app.services.ai_model_service import ai_model_service

def classify_intent(query: str):
    if "intent_classifier" not in ai_model_service.models:
        return "기타"
    res = ai_model_service.classify_intent(query)
    return res[0]["label"]

def classify_complexity(query: str):
    # 간단 규칙 기반 유지 or 별도 분류기 모델 도입
    if any(k in query for k in ["상위","하위","브랜드별","월별","분포"]):
        return "중간"
    if any(k in query for k in ["상관관계","상세 리포트","연관"]):
        return "복잡"
    return "단순"


def build_prompt(query: str, mongo_summary: str, contexts: list[str]):
    context_text = "\n".join(f"- {c}" for c in contexts)
    return (
        f"당신은 무신사 데이터 분석가입니다.\n"
        f"사용자 질문: {query}\n\n"
        f"MongoDB 요약:\n{mongo_summary}\n\n"
        f"관련 컨텍스트:\n{context_text}\n\n"
        f"위 정보를 바탕으로 간결하고 실무적인 답변을 작성하세요.\n"
    )
