from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class LeanCanvas(Base):
    __tablename__ = "lean_canvas"
    
    canvas_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)
    
    # 린 캔버스 9개 요소
    problem = Column(Text)
    customer_segments = Column(Text)
    unique_value_proposition = Column(Text)
    solution = Column(Text)
    unfair_advantage = Column(Text)
    revenue_streams = Column(Text)
    cost_structure = Column(Text)
    key_metrics = Column(Text)
    channels = Column(Text)
    
    canvas_version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계 설정
    project = relationship("Project", backref="lean_canvas")
    
    def __repr__(self):
        return f"<LeanCanvas(canvas_id={self.canvas_id}, project_id={self.project_id})>"