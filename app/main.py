from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, ingest, query, result

app = FastAPI(
    title="Musinsa AI Backend",
    description="Musinsa AI 서비스용 백엔드 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시 도메인 제한 필요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(ingest.router, prefix="/ingest", tags=["Ingest"])
app.include_router(query.router, prefix="/query", tags=["Query"])
app.include_router(result.router, prefix="/result", tags=["Result"])

@app.get("/")
async def root():
    return {"message": "Musinsa AI Backend is running 🚀"}
