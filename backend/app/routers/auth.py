from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserCreateResponse
from app.schemas.common import SuccessResponse, ErrorResponse
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.post("/register", response_model=SuccessResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """회원가입"""
    try:
        print(f"[DEBUG] 회원가입 요청: {user_data}")
        
        # 이메일 중복 확인
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 이메일입니다."
            )
        
        print("[DEBUG] 이메일 중복 확인 완료")
        
        # 비밀번호 해싱
        hashed_password = get_password_hash(user_data.password)
        print("[DEBUG] 비밀번호 해싱 완료")
        
        # 새 사용자 생성
        new_user = User(
            email=user_data.email,
            password_hash=hashed_password,
            name=user_data.name,
            major=user_data.major,
            year=user_data.year
        )
        
        print("[DEBUG] User 객체 생성 완료")
        
        db.add(new_user)
        print("[DEBUG] DB 추가 완료")
        
        db.commit()
        print("[DEBUG] DB 커밋 완료")
        
        db.refresh(new_user)
        print(f"[DEBUG] 새 사용자 ID: {new_user.user_id}")
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": str(new_user.user_id)})
        print("[DEBUG] 토큰 생성 완료")
        
        return SuccessResponse(
            message="회원가입이 완료되었습니다.",
            data=UserCreateResponse(
                user_id=new_user.user_id,
                access_token=access_token
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 회원가입 에러: {str(e)}")
        print(f"[ERROR] 에러 타입: {type(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/login", response_model=SuccessResponse)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """로그인"""
    try:
        # 사용자 조회
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )
        
        # 비밀번호 확인
        if not verify_password(user_credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="이메일 또는 비밀번호가 올바르지 않습니다."
            )
        
        # JWT 토큰 생성
        access_token = create_access_token(data={"sub": str(user.user_id)})
        
        # 사용자 정보 응답 (비밀번호 제외)
        user_response = {
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
            message="로그인에 성공했습니다.",
            data=TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=user_response
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 중 오류가 발생했습니다."
        )

@router.post("/verify-token", response_model=SuccessResponse)
async def verify_token(current_user: dict = Depends(get_current_user)):
    """토큰 검증"""
    return SuccessResponse(
        message="유효한 토큰입니다.",
        data={"user_id": current_user["user_id"]}
    )

@router.get("/test")
async def test_auth():
    """인증 라우터 테스트"""
    return {"message": "Auth router working"}