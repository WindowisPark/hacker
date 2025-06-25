# backend/app/main.py 업데이트
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# 모든 모델 import (테이블 생성을 위해)
from app.models import *

# 라우터 import
from app.routers import auth, users, projects, ai_reports, lean_canvas, team_matching, resumes, dashboard

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(ai_reports.router, prefix="/ai-reports", tags=["AI Reports"])
app.include_router(lean_canvas.router, prefix="/lean-canvas", tags=["lean-canvas"])
app.include_router(team_matching.router, prefix="/team", tags=["Team Matching"])
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])  # 새로 추가
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])  # 새로 추가

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "세종 스타트업 네비게이터 API"}

@app.get("/")
async def root():
    return {"message": "세종 스타트업 네비게이터 API에 오신 것을 환영합니다!"}
