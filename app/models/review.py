from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class Review(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    userId: str
    productId: str
    content: str
    rating: int = Field(ge=1, le=5)
    features: Optional[Dict[str, Any]] = None   # 예: 감성/카테고리 등
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
