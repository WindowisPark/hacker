# backend/app/models/__init__.py 업데이트
# 모든 모델들을 import 해서 SQLAlchemy가 인식할 수 있도록 함
from .user import User
from .project import Project
from .lean_canvas import LeanCanvas
from .team_matching import TeamOpening, TeamApplication
from .ai_report import AIReport
from .resume import Resume
from .research_lab import Department, Professor, ResearchLab, ProjectLabMatching  # 새로 추가

# __all__로 export할 모델들 정의
__all__ = [
    "User",
    "Project", 
    "LeanCanvas",
    "TeamOpening",
    "TeamApplication",
    "AIReport",
    "Resume",
    "Department",      # 새로 추가
    "Professor",       # 새로 추가
    "ResearchLab",     # 새로 추가
    "ProjectLabMatching"  # 새로 추가
]