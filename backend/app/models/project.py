from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    project_id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    idea_name = Column(String(200))
    service_type = Column(String(50), nullable=False)  # APP, WEB, ETC
    target_type = Column(String(50), nullable=False)   # B2C, B2B, ETC
    stage = Column(String(50), default="IDEA")  # IDEA, PROTOTYPE, MVP, BETA, LAUNCH
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # 새로 추가: 공개/비공개 설정
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    owner = relationship("User", backref="owned_projects")
    
    def __repr__(self):
        return f"<Project(project_id={self.project_id}, name={self.name}, owner_id={self.owner_id})>"