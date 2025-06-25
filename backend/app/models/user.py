from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    major = Column(String(100))
    year = Column(Integer)
    user_type = Column(String(50))  # DREAMER, BUILDER, SPECIALIST
    profile_info = Column(String)
    sejong_student_id = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email}, name={self.name})>"