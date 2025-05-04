from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import get_settings
from app.api.routes import router as api_router

app = FastAPI(
    title="AI Shorts Generator",
    description="자동화된 유튜브 쇼츠 생성 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix="/api")

# 스케줄러 설정
scheduler = BackgroundScheduler()

@app.on_event("startup")
async def startup_event():
    settings = get_settings()
    # 여기에 스케줄러 작업 등록
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

@app.get("/")
async def root():
    return {"message": "AI Shorts Generator API is running"} 