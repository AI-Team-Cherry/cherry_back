from app.db.mongodb import db
from datetime import datetime
from bson import ObjectId
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import json

# === 컬렉션 ===
review_image_collection = db["review_image_path"]
vec_collection = db["image_path_with_vec"]

# === ResNet18 (512차원) ===
resnet = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
resnet.fc = nn.Identity()  # 마지막 FC 제거
resnet.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

def extract_image_features(file) -> list:
    """이미지를 ResNet18 임베딩으로 변환 (512차원)"""
    try:
        img = Image.open(file).convert("RGB")
    except Exception:
        return [0.0] * 512
    tensor = transform(img).unsqueeze(0)
    with torch.no_grad():
        features = resnet(tensor)
    return features.squeeze().numpy().tolist()


# === 업로드 서비스 ===
async def upload_review_image_service(file, product_id: str, user_id: str, review_index: int):
    # 저장할 이미지 이름 규칙 정의
    image_name = f"rimg_{product_id}_{review_index}_{file.filename}"

    # review_image_path 컬렉션에 저장
    doc = {
        "product_id": product_id,
        "user_id": user_id,
        "review_index": review_index,
        "image_name": image_name,
        "createdAt": datetime.utcnow()
    }
    result = await review_image_collection.insert_one(doc)

    # === 이미지 임베딩 추출 후 image_path_with_vec 컬렉션에 저장 ===
    image_vector = extract_image_features(file.file)

    vec_doc = {
        "product_id": product_id,
        "image_file": image_name,
        "image_vector": json.dumps(image_vector),  # JSON string으로 저장
        "createdAt": datetime.utcnow()
    }
    await vec_collection.insert_one(vec_doc)

    # 응답 반환 (ObjectId → str)
    return {
        "file_id": str(result.inserted_id),
        "product_id": product_id,
        "user_id": user_id,
        "review_index": review_index,
        "image_name": image_name,
        "createdAt": doc["createdAt"].isoformat()
    }


async def get_review_image_service(file_id: str):
    """review_image_path에서 이미지 메타데이터 조회"""
    doc = await review_image_collection.find_one({"_id": ObjectId(file_id)})
    if not doc:
        return None

    # ObjectId와 createdAt 변환
    doc["_id"] = str(doc["_id"])
    if "createdAt" in doc:
        doc["createdAt"] = doc["createdAt"].isoformat()
    return doc
