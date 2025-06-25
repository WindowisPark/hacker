from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.team_matching import TeamOpening, TeamApplication
from app.models.project import Project
from app.models.user import User
from app.schemas.team_matching import (
    TeamOpeningCreate, TeamOpeningResponse,
    TeamApplicationCreate, TeamApplicationResponse, TeamApplicationDetail,
    ApplicationStatusUpdate
)
from app.schemas.common import SuccessResponse
from app.auth import get_current_user

# prefix는 main.py에서 설정하므로 여기서는 제외합니다.
router = APIRouter(tags=["Team Matching"])

# --- A. For Project Owners (빌더/드리머) ---

@router.post("/openings/", response_model=SuccessResponse)
async def create_team_opening(
    opening_data: TeamOpeningCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """(빌더/드리머) 팀원 모집 공고 등록"""
    project = db.query(Project).filter(Project.project_id == opening_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    if project.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="프로젝트 소유자만 공고를 등록할 수 있습니다.")

    new_opening = TeamOpening(**opening_data.model_dump())
    db.add(new_opening)
    db.commit()
    db.refresh(new_opening)
    
    return SuccessResponse(
        message="모집 공고가 성공적으로 등록되었습니다.",
        data=TeamOpeningResponse.from_orm(new_opening)
    )

@router.get("/openings/project/{project_id}", response_model=SuccessResponse)
async def get_openings_for_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """(빌더/드리머) 내 프로젝트의 모든 공고 조회"""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    if project.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="프로젝트 소유자만 조회할 수 있습니다.")

    openings = db.query(TeamOpening).filter(TeamOpening.project_id == project_id).all()
    return SuccessResponse(
        message="프로젝트의 모집 공고 목록입니다.",
        data=[TeamOpeningResponse.from_orm(o) for o in openings]
    )

@router.get("/openings/{opening_id}/applications", response_model=SuccessResponse)
async def get_applications_for_opening(
    opening_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """(빌더/드리머) 특정 공고에 지원한 지원자 목록 조회"""
    opening = db.query(TeamOpening).filter(TeamOpening.opening_id == opening_id).first()
    if not opening:
        raise HTTPException(status_code=404, detail="모집 공고를 찾을 수 없습니다.")
    
    project = db.query(Project).filter(Project.project_id == opening.project_id).first()
    if project.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="프로젝트 소유자만 지원자를 조회할 수 있습니다.")

    applications = db.query(TeamApplication).filter(TeamApplication.opening_id == opening_id).all()
    
    application_details = []
    for app in applications:
        applicant_info = db.query(User).filter(User.user_id == app.applicant_id).first()
        if applicant_info:
            detail = TeamApplicationDetail(
                application_id=app.application_id,
                opening_id=app.opening_id,
                applicant_id=app.applicant_id,
                applicant_name=applicant_info.name,
                applicant_major=applicant_info.major,
                applicant_year=applicant_info.year,
                message=app.message,
                portfolio_url=app.portfolio_url,
                expected_commitment=app.expected_commitment,
                available_hours=app.available_hours,
                status=app.status,
                applied_at=app.applied_at
            )
            application_details.append(detail)

    return SuccessResponse(
        message="지원자 목록을 성공적으로 조회했습니다.",
        data=application_details
    )

@router.put("/applications/{application_id}/status", response_model=SuccessResponse)
async def update_application_status(
    application_id: int,
    status_update: ApplicationStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """(빌더/드리머) 지원서 상태 변경 (수락/거절)"""
    application = db.query(TeamApplication).filter(TeamApplication.application_id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="지원서를 찾을 수 없습니다.")

    opening = db.query(TeamOpening).filter(TeamOpening.opening_id == application.opening_id).first()
    project = db.query(Project).filter(Project.project_id == opening.project_id).first()
    if project.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="프로젝트 소유자만 상태를 변경할 수 있습니다.")

    if status_update.status not in ["ACCEPTED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="유효하지 않은 상태 값입니다. 'ACCEPTED' 또는 'REJECTED'를 사용하세요.")

    application.status = status_update.status
    db.commit()
    db.refresh(application)

    # 응답을 위해 지원자 상세 정보 다시 조회
    applicant_info = db.query(User).filter(User.user_id == application.applicant_id).first()
    updated_detail = TeamApplicationDetail(
        application_id=application.application_id,
        opening_id=application.opening_id,
        applicant_id=application.applicant_id,
        applicant_name=applicant_info.name,
        applicant_major=applicant_info.major,
        applicant_year=applicant_info.year,
        message=application.message,
        portfolio_url=application.portfolio_url,
        expected_commitment=application.expected_commitment,
        available_hours=application.available_hours,
        status=application.status,
        applied_at=application.applied_at
    )
    
    return SuccessResponse(message="지원서 상태가 성공적으로 변경되었습니다.", data=updated_detail)


# --- B. For Applicants (스페셜리스트) ---

@router.get("/openings/", response_model=SuccessResponse)
async def get_all_openings(db: Session = Depends(get_db)):
    """(스페셜리스트) 전체 모집 공고 목록 조회"""
    openings = db.query(TeamOpening).filter(TeamOpening.status == "OPEN").order_by(TeamOpening.created_at.desc()).all()
    return SuccessResponse(
        message="전체 모집 공고 목록입니다.",
        data=[TeamOpeningResponse.from_orm(o) for o in openings]
    )

@router.get("/openings/{opening_id}", response_model=SuccessResponse)
async def get_opening_detail(opening_id: int, db: Session = Depends(get_db)):
    """(스페셜리스트) 모집 공고 상세 조회"""
    opening = db.query(TeamOpening).filter(TeamOpening.opening_id == opening_id).first()
    if not opening:
        raise HTTPException(status_code=404, detail="모집 공고를 찾을 수 없습니다.")
    return SuccessResponse(
        message="모집 공고 상세 정보입니다.",
        data=TeamOpeningResponse.from_orm(opening)
    )

@router.post("/applications/", response_model=SuccessResponse)
async def apply_to_opening(
    application_data: TeamApplicationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """(스페셜리스트) 팀 지원하기"""
    opening = db.query(TeamOpening).filter(TeamOpening.opening_id == application_data.opening_id).first()
    if not opening or opening.status != "OPEN":
        raise HTTPException(status_code=404, detail="모집 중인 공고가 아닙니다.")

    # 중복 지원 방지
    existing_application = db.query(TeamApplication).filter(
        TeamApplication.opening_id == application_data.opening_id,
        TeamApplication.applicant_id == current_user["user_id"]
    ).first()
    if existing_application:
        raise HTTPException(status_code=400, detail="이미 이 공고에 지원했습니다.")

    new_application_data = application_data.model_dump()
    new_application_data["applicant_id"] = current_user["user_id"]
    
    new_application = TeamApplication(**new_application_data)
    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return SuccessResponse(
        message="성공적으로 지원했습니다.",
        data=TeamApplicationResponse.from_orm(new_application)
    )

@router.get("/applications/my", response_model=SuccessResponse)
async def get_my_applications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """(스페셜리스트) 내 지원 현황 조회"""
    my_applications = db.query(TeamApplication).filter(TeamApplication.applicant_id == current_user["user_id"]).all()
    return SuccessResponse(
        message="나의 지원 현황 목록입니다.",
        data=[TeamApplicationResponse.from_orm(app) for app in my_applications]
    )
