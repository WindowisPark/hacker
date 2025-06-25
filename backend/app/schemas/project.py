from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 프로젝트 생성 요청
class ProjectCreate(BaseModel):
    name: str
    description: str
    idea_name: Optional[str] = None
    service_type: str  # APP, WEB, ETC
    target_type: str   # B2C, B2B, ETC

# 프로젝트 응답
class ProjectResponse(BaseModel):
    project_id: int
    owner_id: int
    name: str
    description: str
    idea_name: Optional[str] = None
    service_type: str
    target_type: str
    stage: str = "IDEA"
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True

# 프로젝트 업데이트
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stage: Optional[str] = None  # IDEA, PROTOTYPE, MVP, BETA, LAUNCH

# 공개 프로젝트 리스트용 (간단한 정보만)
class ProjectPublic(BaseModel):
    project_id: int
    name: str
    description: str
    service_type: str
    target_type: str
    stage: str
    created_at: datetime

    class Config:
        from_attributes = True