# backend/app/models/research_lab.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Department(Base):
    """학과 정보"""
    __tablename__ = "departments"
    
    department_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # 컴퓨터공학과
    name_en = Column(String(200))  # Computer Science and Engineering
    college = Column(String(200), default="인공지능융합대학")  # 소속 대학
    description = Column(Text)  # 학과 설명
    building = Column(String(100))  # 주요 건물 (대양AI센터)
    phone = Column(String(50))
    email = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    professors = relationship("Professor", back_populates="department")
    
    def __repr__(self):
        return f"<Department(name={self.name})>"

class Professor(Base):
    """교수 정보"""
    __tablename__ = "professors"
    
    professor_id = Column(Integer, primary_key=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.department_id"), nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    position = Column(String(50))  # 교수, 부교수, 조교수, 석좌교수
    email = Column(String(200))
    phone = Column(String(50))
    office_location = Column(String(200))  # 대양AI센터 823호
    research_fields = Column(Text)  # 주요 연구분야 (JSON 또는 comma-separated)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    department = relationship("Department", back_populates="professors")
    labs = relationship("ResearchLab", back_populates="director")
    
    def __repr__(self):
        return f"<Professor(name={self.name}, position={self.position})>"

class ResearchLab(Base):
    """연구실 정보"""
    __tablename__ = "research_labs"
    
    lab_id = Column(Integer, primary_key=True, index=True)
    director_id = Column(Integer, ForeignKey("professors.professor_id"), nullable=False)
    name = Column(String(200), nullable=False)  # 지능형 미디어 연구실
    name_en = Column(String(200))  # Intelligent Media Lab
    location = Column(String(200))  # 대양AI센터 622호
    phone = Column(String(50))
    email = Column(String(200))
    website = Column(String(500))
    
    # 연구 분야 및 키워드
    research_areas = Column(Text)  # JSON 형태로 저장
    keywords = Column(Text)  # 검색용 키워드들
    description = Column(Text)  # 연구실 소개
    
    # 매칭을 위한 메타데이터
    tech_stack = Column(Text)  # 사용 기술스택 (JSON)
    collaboration_history = Column(Text)  # 협력 이력 (JSON)
    recent_projects = Column(Text)  # 최근 프로젝트 (JSON)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    director = relationship("Professor", back_populates="labs")
    
    def __repr__(self):
        return f"<ResearchLab(name={self.name})>"

class ProjectLabMatching(Base):
    """프로젝트-연구실 매칭 결과"""
    __tablename__ = "project_lab_matchings"
    
    matching_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    lab_id = Column(Integer, ForeignKey("research_labs.lab_id"), nullable=False)
    
    # 매칭 점수 및 근거
    similarity_score = Column(Float)  # 0.0 ~ 1.0
    matching_reason = Column(Text)  # 매칭 근거 설명
    matching_factors = Column(Text)  # 매칭 요소들 (JSON)
    
    # 상태 관리
    status = Column(String(50), default="SUGGESTED")  # SUGGESTED, CONTACTED, INTERESTED, DECLINED
    contacted_at = Column(DateTime(timezone=True))
    response_at = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    project = relationship("Project")
    lab = relationship("ResearchLab")
    
    def __repr__(self):
        return f"<ProjectLabMatching(project_id={self.project_id}, lab_id={self.lab_id}, score={self.similarity_score})>"