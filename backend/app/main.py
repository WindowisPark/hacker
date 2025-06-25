# backend/app/main.py 업데이트
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# 모든 모델 import (테이블 생성을 위해)
from app.models import *

# 라우터 import
from app.routers import (
    auth, users, projects, ai_reports, lean_canvas, 
    team_matching, resumes, dashboard, research_labs  # 새로 추가
)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="세종 스타트업 네비게이터 API",
    description="해커톤 MVP + 연구실 매칭 시스템",
    version="1.1.0"
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
app.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(research_labs.router, prefix="/research-labs", tags=["Research Labs"])  # 새로 추가

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "세종 스타트업 네비게이터 + 연구실 매칭 API"}

@app.get("/")
async def root():
    return {"message": "세종 스타트업 네비게이터 + 연구실 매칭 API에 오신 것을 환영합니다!"}

@app.get("/api/info")
async def api_info():
    """API 정보 및 새로운 기능 안내"""
    return {
        "service_name": "세종 스타트업 네비게이터",
        "version": "1.1.0",
        "new_features": [
            "연구실 데이터베이스 통합",
            "AI 기반 프로젝트-연구실 매칭",
            "세종대 인공지능융합대학 연구실 정보",
            "협력 연구 추천 시스템"
        ],
        "research_labs": {
            "total_departments": "7개 학과",
            "total_labs": "20+ 연구실",
            "matching_algorithm": "AI 기반 유사도 분석"
        }
    }