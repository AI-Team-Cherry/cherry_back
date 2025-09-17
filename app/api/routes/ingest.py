from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import os, uuid
from app.db.mongodb import reviews_collection, images_collection
from app.services.review_feature import analyze_review
from app.services.ctr_score import score_from_features

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/review")
async def ingest_review(
    userId: str = Form(...),
    productId: str = Form(...),
    content: str = Form(...),
    rating: int = Form(5)
):
    features = await analyze_review(content)
    doc = {
        "userId": userId,
        "productId": productId,
        "content": content,
        "rating": rating,
        "features": features
    }
    await reviews_collection.insert_one(doc)
    return {"status": "ok", "ingested": {"type": "review", "features": features}}

@router.post("/image")
async def ingest_image(
    userId: str = Form(...),
    productId: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    # 파일 저장
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    fname = f"{uuid.uuid4().hex}{ext}"
    fpath = os.path.join(UPLOAD_DIR, fname)
    with open(fpath, "wb") as f:
        f.write(await file.read())

    # 피처 + 점수화
    features = await analyze_image(fpath)
    ctr = score_from_features(features)

    doc = {
        "userId": userId,
        "productId": productId,
        "filePath": fpath,
        "features": features,
        "ctrScore": ctr
    }
    await images_collection.insert_one(doc)
    return {"status": "ok", "ingested": {"type": "image", "filePath": fpath, "features": features, "ctrScore": ctr}}
