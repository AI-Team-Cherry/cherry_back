# app/api/routes/ingest.py

from fastapi import APIRouter

router = APIRouter()

@router.post("/upload")
async def upload_data():
    return {"message": "데이터 업로드 성공!"}
