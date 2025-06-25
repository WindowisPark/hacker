# backend/app/routers/resumes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
from typing import List

from app.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeCreateUpdate, ResumeResponse, ResumePublicResponse
from app.schemas.common import SuccessResponse
from app.auth import get_current_user

router = APIRouter(tags=["Resumes"])

@router.post("/", response_model=SuccessResponse)
async def create_or_update_resume(
    resume_data: ResumeCreateUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """이력서 생성 또는 업데이트 (Upsert)"""
    try:
        # 기존 이력서 조회
        resume = db.query(Resume).filter(Resume.user_id == current_user["user_id"]).first()
        
        # JSON 직렬화
        tech_stack_json = json.dumps([item.model_dump() for item in resume_data.tech_stack], ensure_ascii=False)
        work_experience_json = json.dumps([item.model_dump() for item in resume_data.work_experience], ensure_ascii=False)
        awards_json = json.dumps([item.model_dump() for item in resume_data.awards], ensure_ascii=False)
        external_links_json = json.dumps([item.model_dump() for item in resume_data.external_links], ensure_ascii=False)
        
        if resume:
            # 업데이트
            resume.introduction = resume_data.introduction
            resume.tech_stack = tech_stack_json
            resume.work_experience = work_experience_json
            resume.awards = awards_json
            resume.external_links = external_links_json
        else:
            # 생성
            resume = Resume(
                user_id=current_user["user_id"],
                introduction=resume_data.introduction,
                tech_stack=tech_stack_json,
                work_experience=work_experience_json,
                awards=awards_json,
                external_links=external_links_json
            )
            db.add(resume)
        
        db.commit()
        db.refresh(resume)
        
        return SuccessResponse(
            message="이력서가 성공적으로 저장되었습니다.",
            data={"resume_id": resume.resume_id}
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이력서 저장 중 오류: {str(e)}"
        )

@router.get("/me", response_model=SuccessResponse)
async def get_my_resume(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """내 이력서 조회"""
    try:
        resume = db.query(Resume).filter(Resume.user_id == current_user["user_id"]).first()
        user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이력서를 찾을 수 없습니다."
            )
        
        # JSON 파싱
        tech_stack = json.loads(resume.tech_stack) if resume.tech_stack else []
        work_experience = json.loads(resume.work_experience) if resume.work_experience else []
        awards = json.loads(resume.awards) if resume.awards else []
        external_links = json.loads(resume.external_links) if resume.external_links else []
        
        response_data = ResumeResponse(
            resume_id=resume.resume_id,
            user_id=resume.user_id,
            name=user.name,
            email=user.email,
            major=user.major,
            year=user.year,
            sejong_student_id=user.sejong_student_id,
            introduction=resume.introduction,
            tech_stack=tech_stack,
            work_experience=work_experience,
            awards=awards,
            external_links=external_links,
            created_at=resume.created_at,
            updated_at=resume.updated_at
        )
        
        return SuccessResponse(
            message="이력서 조회에 성공했습니다.",
            data=response_data.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이력서 조회 중 오류: {str(e)}"
        )

@router.get("/{user_id}", response_model=SuccessResponse)
async def get_user_resume(user_id: int, db: Session = Depends(get_db)):
    """다른 사용자 이력서 조회 (공개 정보만)"""
    try:
        resume = db.query(Resume).filter(Resume.user_id == user_id).first()
        user = db.query(User).filter(User.user_id == user_id).first()
        
        if not resume or not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이력서를 찾을 수 없습니다."
            )
        
        # JSON 파싱
        tech_stack = json.loads(resume.tech_stack) if resume.tech_stack else []
        work_experience = json.loads(resume.work_experience) if resume.work_experience else []
        awards = json.loads(resume.awards) if resume.awards else []
        external_links = json.loads(resume.external_links) if resume.external_links else []
        
        response_data = ResumePublicResponse(
            resume_id=resume.resume_id,
            user_id=resume.user_id,
            name=user.name,
            major=user.major,
            year=user.year,
            introduction=resume.introduction,
            tech_stack=tech_stack,
            work_experience=work_experience,
            awards=awards,
            external_links=external_links,
            updated_at=resume.updated_at
        )
        
        return SuccessResponse(
            message="이력서 조회에 성공했습니다.",
            data=response_data.model_dump()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이력서 조회 중 오류: {str(e)}"
        )

@router.delete("/", response_model=SuccessResponse)
async def delete_my_resume(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """내 이력서 삭제"""
    try:
        resume = db.query(Resume).filter(Resume.user_id == current_user["user_id"]).first()
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="이력서를 찾을 수 없습니다."
            )
        
        db.delete(resume)
        db.commit()
        
        return SuccessResponse(
            message="이력서가 성공적으로 삭제되었습니다.",
            data={}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"이력서 삭제 중 오류: {str(e)}"
        )