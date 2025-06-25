from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# 모든 모델 import (테이블 생성을 위해)
from app.models import *

# 라우터 import
from app.routers import auth, users, projects

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="세종 스타트업 네비게이터 API",
    description="해커톤 MVP용 FastAPI",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용, 운영에서는 구체적인 도메인 설정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])

# 추후 활성화 예정
# app.include_router(lean_canvas.router, prefix="/lean-canvas", tags=["lean-canvas"])
# app.include_router(ai_reports.router, prefix="/ai-reports", tags=["ai-reports"])
# app.include_router(team_matching.router, prefix="/team", tags=["team-matching"])
# app.include_router(labs.router, prefix="/labs", tags=["labs"])
# app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "세종 스타트업 네비게이터 API"}

@app.get("/")
async def root():
    return {"message": "세종 스타트업 네비게이터 API에 오신 것을 환영합니다!"}