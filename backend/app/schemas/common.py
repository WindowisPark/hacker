from pydantic import BaseModel
from typing import Any, Optional

# 표준 성공 응답
class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None

# 표준 에러 응답
class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None

# 페이지네이션 응답
class PaginatedResponse(BaseModel):
    success: bool = True
    message: str
    data: list
    total: int
    page: int
    per_page: int
    total_pages: int

# 헬스체크 응답
class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str