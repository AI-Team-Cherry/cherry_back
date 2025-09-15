from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta or config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
    except JWTError:
        return None
