# backend/app/schemas/dashboard.py
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

# 개인 대시보드 통계
class PersonalStats(BaseModel):
    total_projects: int
    active_projects: int
    public_projects: int
    private_projects: int
    projects_by_stage: Dict[str, int]  # {"IDEA": 3, "MVP": 1, ...}
    
    # 팀 매칭 관련
    team_openings_created: int
    applications_received: int
    applications_sent: int
    accepted_applications: int

# 전체 플랫폼 통계
class PlatformStats(BaseModel):
    total_users: int
    total_projects: int
    total_public_projects: int
    recent_users_count: int  # 최근 30일
    recent_projects_count: int  # 최근 30일
    
    # 프로젝트 분포
    projects_by_service_type: Dict[str, int]
    projects_by_target_type: Dict[str, int]
    projects_by_stage: Dict[str, int]
    
    # 사용자 분포
    users_by_type: Dict[str, int]  # {"DREAMER": 10, "BUILDER": 15, ...}
    users_by_major: Dict[str, int]

# 최근 활동
class RecentActivity(BaseModel):
    recent_projects: List[Dict]  # 최근 생성된 프로젝트들
    recent_team_openings: List[Dict]  # 최근 팀 모집 공고들
    recent_applications: List[Dict]  # 최근 지원 현황

# 대시보드 종합 응답
class DashboardResponse(BaseModel):
    personal_stats: PersonalStats
    recent_activity: RecentActivity