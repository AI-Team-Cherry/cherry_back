from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ImageDoc(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    userId: str
    productId: Optional[str] = None
    filePath: str
    features: Optional[Dict[str, Any]] = None   # 예: dominant_color, composition_score 등
    ctrScore: Optional[float] = None            # 매력도/CTR 점수
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
