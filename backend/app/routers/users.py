from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserTypeUpdate, UserProfileUpdate
from app.schemas.common import SuccessResponse
from app.auth import get_current_user

router = APIRouter()

@router.get("/me", response_model=SuccessResponse)
async def get_my_profile(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """내 프로필 조회"""
    try:
        user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        user_data = {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "major": user.major,
            "year": user.year,
            "user_type": user.user_type,
            "profile_info": user.profile_info,
            "sejong_student_id": user.sejong_student_id,
            "created_at": user.created_at
        }
        
        return SuccessResponse(
            message="프로필 조회에 성공했습니다.",
            data=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 조회 중 오류가 발생했습니다."
        )
    
@router.put("/me/profile", response_model=SuccessResponse)
async def update_my_profile(
    profile_data: UserProfileUpdate,
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """프로필 정보 업데이트"""
    try:
        user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        # 업데이트할 필드만 수정
        update_data = profile_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        # 업데이트된 사용자 정보 반환
        user_data = {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "major": user.major,
            "year": user.year,
            "user_type": user.user_type,
            "profile_info": user.profile_info,
            "sejong_student_id": user.sejong_student_id,
            "created_at": user.created_at
        }
        
        return SuccessResponse(
            message="프로필이 성공적으로 업데이트되었습니다.",
            data=user_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 업데이트 중 오류가 발생했습니다."
        )
    
@router.put("/me/type", response_model=SuccessResponse)
async def update_user_type(
    user_type_data: UserTypeUpdate, 
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """사용자 타입 설정 (DREAMER, BUILDER, SPECIALIST)"""
    try:
        # 유효한 사용자 타입인지 확인
        valid_types = ["DREAMER", "BUILDER", "SPECIALIST"]
        if user_type_data.user_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 사용자 타입입니다. 가능한 값: {', '.join(valid_types)}"
            )
        
        # 사용자 조회 및 업데이트
        user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        # 사용자 타입 업데이트
        user.user_type = user_type_data.user_type
        db.commit()
        db.refresh(user)
        
        return SuccessResponse(
            message=f"사용자 타입이 {user_type_data.user_type}로 설정되었습니다.",
            data={"user_type": user.user_type}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 타입 업데이트 중 오류가 발생했습니다."
        )

@router.get("/profile/{user_id}", response_model=SuccessResponse)
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """다른 사용자 프로필 조회 (공개 정보만)"""
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        # 공개 정보만 반환 (이메일 등 민감 정보 제외)
        public_data = {
            "user_id": user.user_id,
            "name": user.name,
            "major": user.major,
            "year": user.year,
            "user_type": user.user_type,
            "created_at": user.created_at
        }
        
        return SuccessResponse(
            message="사용자 프로필 조회에 성공했습니다.",
            data=public_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 프로필 조회 중 오류가 발생했습니다."
        )

@router.get("/test")
async def test_users():
    """사용자 라우터 테스트"""
    return {"message": "Users router working"}