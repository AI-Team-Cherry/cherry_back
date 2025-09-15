from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[str]
    employeeId: str
    name: str
    department: Optional[str] = None
    role: str = "user"
    password: str
    lastLogin: Optional[datetime] = None

class UserOut(BaseModel):
    id: str
    employeeId: str
    name: str
    department: Optional[str] = None
    role: str
    lastLogin: Optional[datetime]
