from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 린 캔버스 생성/업데이트 요청
class LeanCanvasCreate(BaseModel):
    project_id: int
    problem: Optional[str] = None
    customer_segments: Optional[str] = None
    unique_value_proposition: Optional[str] = None
    solution: Optional[str] = None
    unfair_advantage: Optional[str] = None
    revenue_streams: Optional[str] = None
    cost_structure: Optional[str] = None
    key_metrics: Optional[str] = None
    channels: Optional[str] = None

# 린 캔버스 업데이트 (project_id 제외)
class LeanCanvasUpdate(BaseModel):
    problem: Optional[str] = None
    customer_segments: Optional[str] = None
    unique_value_proposition: Optional[str] = None
    solution: Optional[str] = None
    unfair_advantage: Optional[str] = None
    revenue_streams: Optional[str] = None
    cost_structure: Optional[str] = None
    key_metrics: Optional[str] = None
    channels: Optional[str] = None

# 린 캔버스 응답
class LeanCanvasResponse(BaseModel):
    canvas_id: int
    project_id: int
    problem: Optional[str] = None
    customer_segments: Optional[str] = None
    unique_value_proposition: Optional[str] = None
    solution: Optional[str] = None
    unfair_advantage: Optional[str] = None
    revenue_streams: Optional[str] = None
    cost_structure: Optional[str] = None
    key_metrics: Optional[str] = None
    channels: Optional[str] = None
    canvas_version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True