# backend/app/schemas/research_lab.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# 학과 스키마
class DepartmentBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    college: str = "인공지능융합대학"
    description: Optional[str] = None
    building: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentResponse(DepartmentBase):
    department_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 교수 스키마
class ProfessorBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    position: str  # 교수, 부교수, 조교수 등
    email: Optional[str] = None
    phone: Optional[str] = None
    office_location: Optional[str] = None
    research_fields: Optional[str] = None

class ProfessorCreate(ProfessorBase):
    department_id: int

class ProfessorResponse(ProfessorBase):
    professor_id: int
    department_id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# 연구실 스키마
class ResearchLabBase(BaseModel):
    name: str
    name_en: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    research_areas: Optional[str] = None  # JSON string
    keywords: Optional[str] = None
    description: Optional[str] = None
    tech_stack: Optional[str] = None  # JSON string
    collaboration_history: Optional[str] = None  # JSON string
    recent_projects: Optional[str] = None  # JSON string

class ResearchLabCreate(ResearchLabBase):
    director_id: int

class ResearchLabUpdate(ResearchLabBase):
    pass

class ResearchLabResponse(ResearchLabBase):
    lab_id: int
    director_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # 관련 정보
    director_name: Optional[str] = None
    department_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# 매칭 스키마
class ProjectLabMatchingBase(BaseModel):
    similarity_score: float
    matching_reason: Optional[str] = None
    matching_factors: Optional[str] = None  # JSON string

class ProjectLabMatchingCreate(ProjectLabMatchingBase):
    project_id: int
    lab_id: int

class ProjectLabMatchingResponse(ProjectLabMatchingBase):
    matching_id: int
    project_id: int
    lab_id: int
    status: str
    contacted_at: Optional[datetime] = None
    response_at: Optional[datetime] = None
    created_at: datetime
    
    # 관련 정보
    lab_name: Optional[str] = None
    director_name: Optional[str] = None
    department_name: Optional[str] = None
    project_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# 연구실 검색 및 매칭 요청
class LabSearchRequest(BaseModel):
    query: Optional[str] = None
    research_areas: Optional[List[str]] = None
    tech_stack: Optional[List[str]] = None
    department: Optional[str] = None
    limit: int = 10

class ProjectMatchingRequest(BaseModel):
    project_id: int
    max_results: int = 10
    min_score: float = 0.3

class ProjectMatchingResponse(BaseModel):
    project_id: int
    project_name: str
    project_description: str
    matches: List[ProjectLabMatchingResponse]
    
class LabMatchingStatusUpdate(BaseModel):
    status: str  # CONTACTED, INTERESTED, DECLINED
    notes: Optional[str] = None