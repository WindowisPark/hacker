from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 팀원 모집 공고 생성
class TeamOpeningCreate(BaseModel):
    project_id: int
    role_name: str
    description: str
    required_skills: Optional[str] = None
    commitment_type: Optional[str] = None  # FULL_TIME, PART_TIME, INTERNSHIP

# 팀원 모집 공고 응답
class TeamOpeningResponse(BaseModel):
    opening_id: int
    project_id: int
    role_name: str
    description: str
    required_skills: Optional[str] = None
    commitment_type: Optional[str] = None
    status: str = "OPEN"
    created_at: datetime

    class Config:
        from_attributes = True

# 팀 지원 요청
class TeamApplicationCreate(BaseModel):
    opening_id: int
    message: str
    portfolio_url: Optional[str] = None
    expected_commitment: Optional[str] = None  # FULL_TIME, PART_TIME, PROJECT_BASED
    available_hours: Optional[int] = None

# 팀 지원 응답
class TeamApplicationResponse(BaseModel):
    application_id: int
    opening_id: int
    applicant_id: int
    message: str
    portfolio_url: Optional[str] = None
    expected_commitment: Optional[str] = None
    available_hours: Optional[int] = None
    status: str = "PENDING"
    applied_at: datetime

    class Config:
        from_attributes = True

# 지원자 상세 정보 (Builder가 볼 때)
class TeamApplicationDetail(BaseModel):
    application_id: int
    opening_id: int
    applicant_id: int
    applicant_name: str
    applicant_major: Optional[str] = None
    applicant_year: Optional[int] = None
    message: str
    portfolio_url: Optional[str] = None
    expected_commitment: Optional[str] = None
    available_hours: Optional[int] = None
    status: str
    applied_at: datetime

# 지원서 상태 변경
class ApplicationStatusUpdate(BaseModel):
    status: str  # ACCEPTED, REJECTED
    message: Optional[str] = None