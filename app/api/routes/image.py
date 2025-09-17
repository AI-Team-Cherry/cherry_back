from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.image_service import upload_review_image_service, get_review_image_service

router = APIRouter(prefix="/review-images", tags=["review-images"])

@router.post("/upload")
async def upload_review_image(
    file: UploadFile = File(...),
    product_id: str = Form(...),
    user_id: str = Form(...),
    review_index: int = Form(...)
):
    return await upload_review_image_service(file, product_id, user_id, review_index)

@router.get("/{file_id}")
async def get_review_image(file_id: str):
    result = await get_review_image_service(file_id)
    if not result:
        raise HTTPException(status_code=404, detail="Image not found")
    return result
