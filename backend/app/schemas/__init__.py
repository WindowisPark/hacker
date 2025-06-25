# 모든 스키마들을 import
from .user import (
    UserRegister,
    UserLogin,
    UserTypeUpdate,
    UserResponse,
    TokenResponse,
    UserCreateResponse
)

from .project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectPublic
)

from .lean_canvas import (
    LeanCanvasCreate,
    LeanCanvasUpdate,
    LeanCanvasResponse
)

from .team_matching import (
    TeamOpeningCreate,
    TeamOpeningResponse,
    TeamApplicationCreate,
    TeamApplicationResponse,
    TeamApplicationDetail,
    ApplicationStatusUpdate
)

from .ai_report import (
    AIReportRequest,
    AIReportResponse,
    AIReportStatus,
    AIReportFeedback,
    IdeaInfo,
    ExistingServices,
    NewIdea
)

from .common import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    HealthResponse
)

# __all__로 export할 스키마들 정의
__all__ = [
    # User schemas
    "UserRegister", "UserLogin", "UserTypeUpdate", "UserResponse", 
    "TokenResponse", "UserCreateResponse",
    
    # Project schemas
    "ProjectCreate", "ProjectResponse", "ProjectUpdate", "ProjectPublic",
    
    # Lean Canvas schemas
    "LeanCanvasCreate", "LeanCanvasUpdate", "LeanCanvasResponse",
    
    # Team Matching schemas
    "TeamOpeningCreate", "TeamOpeningResponse", "TeamApplicationCreate",
    "TeamApplicationResponse", "TeamApplicationDetail", "ApplicationStatusUpdate",
    
    # AI Report schemas
    "AIReportRequest", "AIReportResponse", "AIReportStatus", "AIReportFeedback",
    "IdeaInfo", "ExistingServices", "NewIdea",
    
    # Common schemas
    "SuccessResponse", "ErrorResponse", "PaginatedResponse", "HealthResponse"
]