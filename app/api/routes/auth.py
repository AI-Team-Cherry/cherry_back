from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.db.mongodb import db
from app.models.user import User, UserOut, UserIn
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register(user: UserIn):
    # 이미 존재하는 employeeId 체크
    existing = await db.users.find_one({"employeeId": user.employeeId})
    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")

    # 패스워드 해싱
    hashed_pw = hash_password(user.password)

    # MongoDB에 저장할 dict (id 대신 _id)
    doc = {
        "employeeId": user.employeeId,
        "name": user.name,
        "department": user.department,
        "role": user.role,
        "password": hashed_pw,
        "lastLogin": None,
    }
    result = await db.users.insert_one(doc)

    return UserOut(
        id=str(result.inserted_id),
        employeeId=user.employeeId,
        name=user.name,
        department=user.department,
        role=user.role,
        lastLogin=None,
    )

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await db.users.find_one({"employeeId": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user["_id"]), "employeeId": user["employeeId"]})
    return {"access_token": token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/me")
async def get_me(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # DB에서 유저 가져오기
    user = await db.users.find_one({"employeeId": payload.get("employeeId")})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user["_id"]),
        "employeeId": user["employeeId"],
        "name": user.get("name"),
        "department": user.get("department"),
        "role": user.get("role"),
        "lastLogin": user.get("lastLogin"),
    }