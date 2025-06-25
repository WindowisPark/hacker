from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

# AI 보고서 생성 요청
class AIReportRequest(BaseModel):
    project_id: int
    idea_description: str
    industry: str
    target_market: Optional[str] = None

# 아이디어 정보 스키마
class IdeaInfo(BaseModel):
    idea_name: str
    industry: str
    target_market: str

# 기존 서비스 정보 스키마
class ExistingServices(BaseModel):
    name: List[str]
    business_model: List[str]
    marketing: List[str]

# 새로운 아이디어 스키마 (린 캔버스 형태)
class NewIdea(BaseModel):
    problem: str
    customer: str
    solution: str
    unique_value_proposition: str
    unfair_advantage: str
    revenue_stream: str
    cost: str
    key_metric: str
    channels: str

# AI 보고서 응답
class AIReportResponse(BaseModel):
    report_id: int
    project_id: int
    requester_id: int
    report_type: str
    idea_info: Optional[Dict[str, Any]] = None
    existing_services: Optional[Dict[str, Any]] = None
    service_limitations: Optional[str] = None
    lean_canvas_detailed: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    data_sources: Optional[str] = None
    generation_time_seconds: Optional[int] = None
    token_usage: Optional[int] = None
    created_at: datetime
    is_latest: bool = True
    user_feedback_rating: Optional[int] = None
    user_feedback_comment: Optional[str] = None

    class Config:
        from_attributes = True

# AI 보고서 생성 진행 상황
class AIReportStatus(BaseModel):
    report_id: int
    status: str  # GENERATING, COMPLETED, FAILED
    progress_percentage: Optional[int] = None
    estimated_time: Optional[int] = None
    error_message: Optional[str] = None

# 피드백 요청
class AIReportFeedback(BaseModel):
    rating: int  # 1-5
    comment: Optional[str] = None