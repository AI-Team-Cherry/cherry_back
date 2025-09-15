from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.db.mongodb import db
from app.models.user import User, UserOut
from app.core.security import hash_password, verify_password, create_access_token
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/register")
async def register(user: User):
    existing = await db.users.find_one({"employeeId": user.employeeId})
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")
    user.password = hash_password(user.password)
    result = await db.users.insert_one(user.dict())
    return {"id": str(result.inserted_id), "message": "등록 성공"}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"employeeId": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="잘못된 아이디/비밀번호")
    token = create_access_token({"sub": str(user["_id"]), "role": user["role"]})
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"lastLogin": datetime.utcnow()}}
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(token: str):
    # 단순화 → 실제 구현은 Depends(OAuth2PasswordBearer) 필요
    return {"message": "현재 사용자 정보 (토큰에서 추출)"}
