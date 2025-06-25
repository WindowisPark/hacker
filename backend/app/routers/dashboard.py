# backend/app/routers/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from typing import Dict, List

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.team_matching import TeamOpening, TeamApplication
from app.models.ai_report import AIReport
from app.schemas.dashboard import PersonalStats, PlatformStats, RecentActivity, DashboardResponse
from app.schemas.common import SuccessResponse
from app.auth import get_current_user

router = APIRouter(tags=["Dashboard"])

@router.get("/personal", response_model=SuccessResponse)
async def get_personal_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """개인 대시보드 통계"""
    try:
        user_id = current_user["user_id"]
        
        # 프로젝트 통계
        total_projects = db.query(Project).filter(
            Project.owner_id == user_id, 
            Project.is_active == True
        ).count()
        
        active_projects = db.query(Project).filter(
            Project.owner_id == user_id,
            Project.is_active == True
        ).count()
        
        public_projects = db.query(Project).filter(
            Project.owner_id == user_id,
            Project.is_active == True,
            Project.is_public == True
        ).count()
        
        private_projects = total_projects - public_projects
        
        # 프로젝트 단계별 분포
        stage_counts = db.query(
            Project.stage, 
            func.count(Project.project_id)
        ).filter(
            Project.owner_id == user_id,
            Project.is_active == True
        ).group_by(Project.stage).all()
        
        projects_by_stage = {stage: count for stage, count in stage_counts}
        
        # 팀 매칭 통계
        team_openings_created = db.query(TeamOpening).join(Project).filter(
            Project.owner_id == user_id
        ).count()
        
        applications_received = db.query(TeamApplication).join(
            TeamOpening
        ).join(Project).filter(
            Project.owner_id == user_id
        ).count()
        
        applications_sent = db.query(TeamApplication).filter(
            TeamApplication.applicant_id == user_id
        ).count()
        
        accepted_applications = db.query(TeamApplication).filter(
            TeamApplication.applicant_id == user_id,
            TeamApplication.status == "ACCEPTED"
        ).count()
        
        # 최근 활동
        # 최근 프로젝트 (내가 만든 것)
        recent_projects = db.query(Project).filter(
            Project.owner_id == user_id,
            Project.is_active == True
        ).order_by(Project.created_at.desc()).limit(5).all()
        
        recent_projects_data = [
            {
                "project_id": p.project_id,
                "name": p.name,
                "stage": p.stage,
                "is_public": p.is_public,
                "created_at": p.created_at
            } for p in recent_projects
        ]
        
        # 최근 팀 모집 공고 (내 프로젝트의)
        recent_openings = db.query(TeamOpening).join(Project).filter(
            Project.owner_id == user_id
        ).order_by(TeamOpening.created_at.desc()).limit(5).all()
        
        recent_openings_data = [
            {
                "opening_id": o.opening_id,
                "role_name": o.role_name,
                "project_name": o.project.name,
                "status": o.status,
                "created_at": o.created_at
            } for o in recent_openings
        ]
        
        # 최근 지원 현황 (내가 지원한 것)
        recent_applications = db.query(TeamApplication).filter(
            TeamApplication.applicant_id == user_id
        ).order_by(TeamApplication.applied_at.desc()).limit(5).all()
        
        recent_applications_data = [
            {
                "application_id": a.application_id,
                "role_name": a.opening.role_name,
                "project_name": a.opening.project.name,
                "status": a.status,
                "applied_at": a.applied_at
            } for a in recent_applications
        ]
        
        personal_stats = PersonalStats(
            total_projects=total_projects,
            active_projects=active_projects,
            public_projects=public_projects,
            private_projects=private_projects,
            projects_by_stage=projects_by_stage,
            team_openings_created=team_openings_created,
            applications_received=applications_received,
            applications_sent=applications_sent,
            accepted_applications=accepted_applications
        )
        
        recent_activity = RecentActivity(
            recent_projects=recent_projects_data,
            recent_team_openings=recent_openings_data,
            recent_applications=recent_applications_data
        )
        
        dashboard_data = DashboardResponse(
            personal_stats=personal_stats,
            recent_activity=recent_activity
        )
        
        return SuccessResponse(
            message="개인 대시보드 조회에 성공했습니다.",
            data=dashboard_data.model_dump()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"대시보드 조회 중 오류: {str(e)}"
        )

@router.get("/platform", response_model=SuccessResponse)
async def get_platform_statistics(db: Session = Depends(get_db)):
    """전체 플랫폼 통계 (공개 정보)"""
    try:
        # 기본 통계
        total_users = db.query(User).count()
        total_projects = db.query(Project).filter(Project.is_active == True).count()
        total_public_projects = db.query(Project).filter(
            Project.is_active == True,
            Project.is_public == True
        ).count()
        
        # 최근 30일 통계
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_users_count = db.query(User).filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        recent_projects_count = db.query(Project).filter(
            Project.created_at >= thirty_days_ago,
            Project.is_active == True
        ).count()
        
        # 프로젝트 서비스 타입별 분포
        service_type_counts = db.query(
            Project.service_type,
            func.count(Project.project_id)
        ).filter(
            Project.is_active == True,
            Project.is_public == True
        ).group_by(Project.service_type).all()
        
        projects_by_service_type = {service_type: count for service_type, count in service_type_counts}
        
        # 프로젝트 타겟 타입별 분포
        target_type_counts = db.query(
            Project.target_type,
            func.count(Project.project_id)
        ).filter(
            Project.is_active == True,
            Project.is_public == True
        ).group_by(Project.target_type).all()
        
        projects_by_target_type = {target_type: count for target_type, count in target_type_counts}
        
        # 프로젝트 단계별 분포
        stage_counts = db.query(
            Project.stage,
            func.count(Project.project_id)
        ).filter(
            Project.is_active == True,
            Project.is_public == True
        ).group_by(Project.stage).all()
        
        projects_by_stage = {stage: count for stage, count in stage_counts}
        
        # 사용자 타입별 분포
        user_type_counts = db.query(
            User.user_type,
            func.count(User.user_id)
        ).filter(
            User.user_type.isnot(None)
        ).group_by(User.user_type).all()
        
        users_by_type = {user_type or "UNDEFINED": count for user_type, count in user_type_counts}
        
        # 전공별 분포 (상위 10개)
        major_counts = db.query(
            User.major,
            func.count(User.user_id)
        ).filter(
            User.major.isnot(None)
        ).group_by(User.major).order_by(
            func.count(User.user_id).desc()
        ).limit(10).all()
        
        users_by_major = {major or "기타": count for major, count in major_counts}
        
        platform_stats = PlatformStats(
            total_users=total_users,
            total_projects=total_projects,
            total_public_projects=total_public_projects,
            recent_users_count=recent_users_count,
            recent_projects_count=recent_projects_count,
            projects_by_service_type=projects_by_service_type,
            projects_by_target_type=projects_by_target_type,
            projects_by_stage=projects_by_stage,
            users_by_type=users_by_type,
            users_by_major=users_by_major
        )
        
        return SuccessResponse(
            message="플랫폼 통계 조회에 성공했습니다.",
            data=platform_stats.model_dump()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"플랫폼 통계 조회 중 오류: {str(e)}"
        )

@router.get("/trending", response_model=SuccessResponse)
async def get_trending_data(db: Session = Depends(get_db)):
    """인기/트렌딩 데이터"""
    try:
        # 최근 7일간 가장 많이 조회된 프로젝트 (실제로는 지원이 많이 들어온 프로젝트로 대체)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        trending_projects = db.query(
            Project.project_id,
            Project.name,
            Project.service_type,
            Project.stage,
            func.count(TeamApplication.application_id).label('application_count')
        ).join(
            TeamOpening, Project.project_id == TeamOpening.project_id
        ).join(
            TeamApplication, TeamOpening.opening_id == TeamApplication.opening_id
        ).filter(
            Project.is_active == True,
            Project.is_public == True,
            TeamApplication.applied_at >= seven_days_ago
        ).group_by(
            Project.project_id
        ).order_by(
            func.count(TeamApplication.application_id).desc()
        ).limit(10).all()
        
        trending_projects_data = [
            {
                "project_id": p.project_id,
                "name": p.name,
                "service_type": p.service_type,
                "stage": p.stage,
                "application_count": p.application_count
            } for p in trending_projects
        ]
        
        # 최근 활발한 모집 공고
        active_openings = db.query(
            TeamOpening.opening_id,
            TeamOpening.role_name,
            Project.name.label('project_name'),
            func.count(TeamApplication.application_id).label('application_count')
        ).join(
            Project, TeamOpening.project_id == Project.project_id
        ).outerjoin(
            TeamApplication, TeamOpening.opening_id == TeamApplication.opening_id
        ).filter(
            TeamOpening.status == "OPEN",
            Project.is_active == True,
            Project.is_public == True
        ).group_by(
            TeamOpening.opening_id
        ).order_by(
            func.count(TeamApplication.application_id).desc()
        ).limit(10).all()
        
        active_openings_data = [
            {
                "opening_id": o.opening_id,
                "role_name": o.role_name,
                "project_name": o.project_name,
                "application_count": o.application_count
            } for o in active_openings
        ]
        
        trending_data = {
            "trending_projects": trending_projects_data,
            "active_openings": active_openings_data
        }
        
        return SuccessResponse(
            message="트렌딩 데이터 조회에 성공했습니다.",
            data=trending_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"트렌딩 데이터 조회 중 오류: {str(e)}"
        )