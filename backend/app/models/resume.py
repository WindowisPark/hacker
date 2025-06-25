# backend/app/models/resume.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Resume(Base):
    __tablename__ = "resumes"
    
    resume_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, unique=True)
    
    # 기본 정보는 User 테이블에서 가져옴
    introduction = Column(Text)  # 자기소개서
    tech_stack = Column(Text)  # 기술 스택 (JSON 문자열로 저장)
    work_experience = Column(Text)  # 업무 경력 (JSON 문자열로 저장)
    awards = Column(Text)  # 수상 이력 (JSON 문자열로 저장)
    external_links = Column(Text)  # 외부 링크 (JSON 문자열로 저장)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    user = relationship("User", backref="resume")
    
    def __repr__(self):
        return f"<Resume(resume_id={self.resume_id}, user_id={self.user_id})>"