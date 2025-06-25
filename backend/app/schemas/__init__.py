# backend/app/schemas/__init__.py 업데이트
# 모든 스키마들을 import
from .user import (
    UserRegister,
    UserLogin,
    UserTypeUpdate,
    UserResponse,
    TokenResponse,
    UserCreateResponse,
    UserProfileUpdate  # 새로 추가
)

from .project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectPublic,
    ProjectPrivacyUpdate  # 새로 추가
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

from .resume import (  # 새로 추가
    ResumeCreateUpdate,
    ResumeResponse,
    ResumePublicResponse,
    TechStackItem,
    WorkExperienceItem,
    AwardItem,
    ExternalLinkItem
)

from .dashboard import (  # 새로 추가
    PersonalStats,
    PlatformStats,
    RecentActivity,
    DashboardResponse
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
    "TokenResponse", "UserCreateResponse", "UserProfileUpdate",
    
    # Project schemas
    "ProjectCreate", "ProjectResponse", "ProjectUpdate", "ProjectPublic",
    "ProjectPrivacyUpdate",
    
    # Lean Canvas schemas
    "LeanCanvasCreate", "LeanCanvasUpdate", "LeanCanvasResponse",
    
    # Team Matching schemas
    "TeamOpeningCreate", "TeamOpeningResponse", "TeamApplicationCreate",
    "TeamApplicationResponse", "TeamApplicationDetail", "ApplicationStatusUpdate",
    
    # AI Report schemas
    "AIReportRequest", "AIReportResponse", "AIReportStatus", "AIReportFeedback",
    "IdeaInfo", "ExistingServices", "NewIdea",
    
    # Resume schemas
    "ResumeCreateUpdate", "ResumeResponse", "ResumePublicResponse",
    "TechStackItem", "WorkExperienceItem", "AwardItem", "ExternalLinkItem",
    
    # Dashboard schemas
    "PersonalStats", "PlatformStats", "RecentActivity", "DashboardResponse",
    
    # Common schemas
    "SuccessResponse", "ErrorResponse", "PaginatedResponse", "HealthResponse"
]