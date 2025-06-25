from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class AIReport(Base):
    __tablename__ = "ai_reports"
    
    report_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    requester_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # LEAN_CANVAS, MARKET_ANALYSIS, IDEA_VALIDATION
    
    # SQLite에서는 JSON을 TEXT로 저장
    idea_info = Column(Text)  # JSON 문자열로 저장
    existing_services = Column(Text)  # JSON 문자열로 저장
    service_limitations = Column(Text)  # JSON 문자열로 저장
    lean_canvas_detailed = Column(Text)  # JSON 문자열로 저장
    
    # 메타데이터
    confidence_score = Column(Float)  # AI 분석 신뢰도 (0.0-1.0)
    data_sources = Column(Text)  # 분석에 사용된 데이터 출처
    generation_time_seconds = Column(Integer)  # 보고서 생성 소요 시간
    token_usage = Column(Integer)  # 사용된 토큰 수
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_latest = Column(Boolean, default=True)
    user_feedback_rating = Column(Integer)  # 사용자 피드백 점수 (1-5)
    user_feedback_comment = Column(Text)
    
    # 관계 설정
    project = relationship("Project", backref="ai_reports")
    requester = relationship("User", backref="requested_reports")
    
    def __repr__(self):
        return f"<AIReport(report_id={self.report_id}, project_id={self.project_id}, type={self.report_type})>"