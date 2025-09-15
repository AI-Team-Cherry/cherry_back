from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Review(BaseModel):
    id: Optional[str]
    userId: str
    productId: str
    content: str
    rating: int
    createdAt: datetime = datetime.utcnow()
