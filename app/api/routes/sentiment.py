from fastapi import APIRouter, UploadFile, File, Body, HTTPException
from typing import Dict, Any
import tempfile
import pandas as pd
import os

from app.services.sentiment_service import analyze_text, analyze_csv, analyze_mongo
from app.services.huggingface_service import debug_model

router = APIRouter(prefix="/sentiment", tags=["Sentiment"])


# ========================
# 🔹 1. 단일 텍스트 분석
# ========================
@router.post("/analyze-text")
async def analyze_single_text(payload: dict = Body(...)):
    """
    JSON body에서 반드시 {"text": "..."} 형태로 받아 처리
    """
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="`text` field is required in JSON body.")

    result = analyze_text(text)
    return {"status": "success", "input": text, "result": result}


# ========================
# 🔹 2. CSV 파일 분석
# ========================
@router.post("/analyze-csv")
async def analyze_csv_file(file: UploadFile = File(...)):
    """
    CSV 파일 업로드 후 감정분석 수행
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    output_path = analyze_csv(tmp_path)
    df = pd.read_csv(output_path)

    return {
        "status": "success",
        "rows": len(df),
        "output_file": os.path.basename(output_path),
        "sample": df.head(5).to_dict(orient="records"),
    }


# ========================
# 🔹 3. MongoDB 리뷰 일괄 분석
# ========================
@router.post("/analyze-mongo")
async def analyze_mongo_reviews(limit: int = 1000):
    """
    MongoDB에서 리뷰 가져와 일괄 감정분석 후 다시 저장
    """
    processed = await analyze_mongo(limit=limit)
    return {"status": "success", "processed": processed}


# ========================
# 🔹 4. 모델 디버그
# ========================
@router.post("/debug-model")
async def debug_sentiment_model(payload: Dict[str, Any] = Body(...)):
    """
    디버그용: 입력 텍스트에 대해 모델 출력 확인
    JSON body에서 {"text": "..."} 로 받음
    """
    text = payload.get("text")
    if not text:
        raise HTTPException(status_code=400, detail="`text` field is required in JSON body.")

    result = debug_model(text)
    return {"status": "success", "input": text, "result": result}
