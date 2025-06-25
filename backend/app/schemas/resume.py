# backend/app/schemas/resume.py
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

# 기술 스택 항목
class TechStackItem(BaseModel):
    name: str
    level: str  # BEGINNER, INTERMEDIATE, ADVANCED, EXPERT

# 업무 경력 항목
class WorkExperienceItem(BaseModel):
    company: str
    position: str
    start_date: str  # YYYY-MM 형식
    end_date: Optional[str] = None  # None이면 현재 재직중
    description: Optional[str] = None

# 수상 이력 항목
class AwardItem(BaseModel):
    title: str
    organization: str
    date: str  # YYYY-MM 형식
    description: Optional[str] = None

# 외부 링크 항목
class ExternalLinkItem(BaseModel):
    type: str  # GITHUB, BLOG, PORTFOLIO, LINKEDIN, etc.
    title: str
    url: str

# 이력서 생성/업데이트 요청
class ResumeCreateUpdate(BaseModel):
    introduction: Optional[str] = None
    tech_stack: Optional[List[TechStackItem]] = []
    work_experience: Optional[List[WorkExperienceItem]] = []
    awards: Optional[List[AwardItem]] = []
    external_links: Optional[List[ExternalLinkItem]] = []

# 이력서 응답 (유저 기본 정보 포함)
class ResumeResponse(BaseModel):
    resume_id: int
    user_id: int
    
    # 유저 기본 정보
    name: str
    email: str
    major: Optional[str] = None
    year: Optional[int] = None
    sejong_student_id: Optional[str] = None
    
    # 이력서 정보
    introduction: Optional[str] = None
    tech_stack: List[TechStackItem] = []
    work_experience: List[WorkExperienceItem] = []
    awards: List[AwardItem] = []
    external_links: List[ExternalLinkItem] = []
    
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 공개용 이력서 (이메일 제외)
class ResumePublicResponse(BaseModel):
    resume_id: int
    user_id: int
    
    # 유저 기본 정보 (이메일 제외)
    name: str
    major: Optional[str] = None
    year: Optional[int] = None
    
    # 이력서 정보
    introduction: Optional[str] = None
    tech_stack: List[TechStackItem] = []
    work_experience: List[WorkExperienceItem] = []
    awards: List[AwardItem] = []
    external_links: List[ExternalLinkItem] = []
    
    updated_at: datetime