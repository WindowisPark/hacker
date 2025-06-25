from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# 회원가입 요청
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    major: str
    year: int

# 로그인 요청
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 사용자 타입 업데이트
class UserTypeUpdate(BaseModel):
    user_type: str  # DREAMER, BUILDER, SPECIALIST

# 사용자 응답 (비밀번호 제외)
class UserResponse(BaseModel):
    user_id: int
    email: str
    name: str
    major: Optional[str] = None
    year: Optional[int] = None
    user_type: Optional[str] = None
    profile_info: Optional[str] = None
    sejong_student_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# 토큰 응답
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# 기본 응답 포맷
class UserCreateResponse(BaseModel):
    user_id: int
    access_token: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    major: Optional[str] = None
    year: Optional[int] = None
    profile_info: Optional[str] = None
    sejong_student_id: Optional[str] = None