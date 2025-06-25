from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class TeamOpening(Base):
    __tablename__ = "team_openings"
    
    opening_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    role_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(Text)
    commitment_type = Column(String(50))  # FULL_TIME, PART_TIME, INTERNSHIP
    status = Column(String(50), default="OPEN")  # OPEN, CLOSED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    project = relationship("Project", backref="team_openings")
    
    def __repr__(self):
        return f"<TeamOpening(opening_id={self.opening_id}, role_name={self.role_name})>"

class TeamApplication(Base):
    __tablename__ = "team_applications"
    
    application_id = Column(Integer, primary_key=True, index=True)
    opening_id = Column(Integer, ForeignKey("team_openings.opening_id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    message = Column(Text, nullable=False)
    portfolio_url = Column(String(500))
    expected_commitment = Column(String(50))  # FULL_TIME, PART_TIME, PROJECT_BASED
    available_hours = Column(Integer)
    status = Column(String(50), default="PENDING")  # PENDING, ACCEPTED, REJECTED
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    
    # 관계 설정
    opening = relationship("TeamOpening", backref="applications")
    applicant = relationship("User", backref="team_applications")
    
    def __repr__(self):
        return f"<TeamApplication(application_id={self.application_id}, applicant_id={self.applicant_id})>"