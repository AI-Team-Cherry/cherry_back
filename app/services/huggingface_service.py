from transformers import pipeline

# 미리 로드된 모델
MODEL_NAME = "solbi12/ecommers_fasion_fine_tuned_3class_model"
sentiment_pipeline = pipeline("text-classification", model=MODEL_NAME, top_k=None)

# 단일 실행
def run_model(text: str):
    preds = sentiment_pipeline(text, truncation=True)[0]  # → list of dicts
    # 가장 높은 score를 가진 결과 선택
    best = max(preds, key=lambda x: x["score"])
    result = {
        "overall_prediction": best["label"],
        "overall_confidence": best["score"],
        "all_classes": preds   # 디버깅/분석용: 전체 클래스 확률도 반환
    }
    return result

# 디버그 전용
def debug_model(text: str):
    return sentiment_pipeline(text, truncation=True)[0]
