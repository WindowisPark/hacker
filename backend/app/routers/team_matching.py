from fastapi import APIRouter, Depends, HTTPException, status, Query  # Query 추가
from sqlalchemy.orm import Session
from sqlalchemy import func  # func도 추가 (통계에서 사용)
from typing import List, Optional  # Optional 추가
from datetime import datetime, timedelta  # datetime, timedelta 추가

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

@router.put("/openings/{opening_id}", response_model=SuccessResponse)
async def update_team_opening(
    opening_id: int,
    opening_update: TeamOpeningCreate,  # 같은 스키마 재사용
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """(빌더/드리머) 팀원 모집 공고 수정"""
    opening = db.query(TeamOpening).filter(TeamOpening.opening_id == opening_id).first()
    if not opening:
        raise HTTPException(status_code=404, detail="모집 공고를 찾을 수 없습니다.")
    
    project = db.query(Project).filter(Project.project_id == opening.project_id).first()
    if project.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="프로젝트 소유자만 공고를 수정할 수 있습니다.")

    # 업데이트
    opening.role_name = opening_update.role_name
    opening.description = opening_update.description
    opening.required_skills = opening_update.required_skills
    opening.commitment_type = opening_update.commitment_type
    
    db.commit()
    db.refresh(opening)
    
    return SuccessResponse(
        message="모집 공고가 성공적으로 수정되었습니다.",
        data=TeamOpeningResponse.from_orm(opening)
    )

@router.delete("/openings/{opening_id}", response_model=SuccessResponse)
async def delete_team_opening(
    opening_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """(빌더/드리머) 팀원 모집 공고 삭제"""
    opening = db.query(TeamOpening).filter(TeamOpening.opening_id == opening_id).first()
    if not opening:
        raise HTTPException(status_code=404, detail="모집 공고를 찾을 수 없습니다.")
    
    project = db.query(Project).filter(Project.project_id == opening.project_id).first()
    if project.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="프로젝트 소유자만 공고를 삭제할 수 있습니다.")

    # 상태를 CLOSED로 변경 (완전 삭제하지 않음)
    opening.status = "CLOSED"
    db.commit()
    
    return SuccessResponse(
        message="모집 공고가 성공적으로 삭제되었습니다.",
        data={"opening_id": opening_id}
    )

@router.delete("/applications/{application_id}", response_model=SuccessResponse)
async def cancel_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """(스페셜리스트) 지원 취소"""
    application = db.query(TeamApplication).filter(TeamApplication.application_id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="지원서를 찾을 수 없습니다.")
    
    if application.applicant_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="본인의 지원서만 취소할 수 있습니다.")
    
    if application.status != "PENDING":
        raise HTTPException(status_code=400, detail="대기 중인 지원서만 취소할 수 있습니다.")

    db.delete(application)
    db.commit()
    
    return SuccessResponse(
        message="지원이 성공적으로 취소되었습니다.",
        data={"application_id": application_id}
    )

@router.get("/openings/search", response_model=SuccessResponse)
async def search_team_openings(
    role: Optional[str] = Query(None, description="역할명으로 검색"),
    skills: Optional[str] = Query(None, description="기술스택으로 검색"),
    commitment: Optional[str] = Query(None, description="커밋먼트 타입 필터"),
    service_type: Optional[str] = Query(None, description="서비스 타입 필터"),
    stage: Optional[str] = Query(None, description="프로젝트 단계 필터"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """(스페셜리스트) 팀원 모집 공고 검색/필터링"""
    query = db.query(TeamOpening).join(Project).filter(
        TeamOpening.status == "OPEN",
        Project.is_active == True,
        Project.is_public == True
    )
    
    if role:
        query = query.filter(TeamOpening.role_name.ilike(f"%{role}%"))
    
    if skills:
        query = query.filter(TeamOpening.required_skills.ilike(f"%{skills}%"))
    
    if commitment:
        query = query.filter(TeamOpening.commitment_type == commitment)
    
    if service_type:
        query = query.filter(Project.service_type == service_type)
    
    if stage:
        query = query.filter(Project.stage == stage)
    
    openings = query.order_by(TeamOpening.created_at.desc()).limit(limit).all()
    
    # 프로젝트 정보도 함께 반환
    openings_with_project = []
    for opening in openings:
        opening_dict = TeamOpeningResponse.from_orm(opening).model_dump()
        opening_dict["project_info"] = {
            "name": opening.project.name,
            "service_type": opening.project.service_type,
            "stage": opening.project.stage,
            "owner_name": opening.project.owner.name
        }
        openings_with_project.append(opening_dict)
    
    return SuccessResponse(
        message=f"검색 결과 {len(openings_with_project)}개의 모집 공고를 찾았습니다.",
        data=openings_with_project
    )

@router.get("/statistics", response_model=SuccessResponse)
async def get_team_matching_statistics(db: Session = Depends(get_db)):
    """팀 매칭 관련 통계"""
    try:
        # 전체 통계
        total_openings = db.query(TeamOpening).count()
        active_openings = db.query(TeamOpening).filter(TeamOpening.status == "OPEN").count()
        total_applications = db.query(TeamApplication).count()
        accepted_applications = db.query(TeamApplication).filter(TeamApplication.status == "ACCEPTED").count()
        
        # 역할별 통계
        role_counts = db.query(
            TeamOpening.role_name,
            func.count(TeamOpening.opening_id)
        ).filter(
            TeamOpening.status == "OPEN"
        ).group_by(TeamOpening.role_name).all()
        
        popular_roles = {role: count for role, count in role_counts}
        
        # 커밋먼트 타입별 통계
        commitment_counts = db.query(
            TeamOpening.commitment_type,
            func.count(TeamOpening.opening_id)
        ).filter(
            TeamOpening.status == "OPEN"
        ).group_by(TeamOpening.commitment_type).all()
        
        commitment_stats = {commitment or "미지정": count for commitment, count in commitment_counts}
        
        # 최근 7일간 활동
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_openings = db.query(TeamOpening).filter(
            TeamOpening.created_at >= seven_days_ago
        ).count()
        
        recent_applications = db.query(TeamApplication).filter(
            TeamApplication.applied_at >= seven_days_ago
        ).count()
        
        statistics = {
            "overview": {
                "total_openings": total_openings,
                "active_openings": active_openings,
                "total_applications": total_applications,
                "accepted_applications": accepted_applications,
                "success_rate": round(accepted_applications / total_applications * 100, 1) if total_applications > 0 else 0
            },
            "popular_roles": popular_roles,
            "commitment_distribution": commitment_stats,
            "recent_activity": {
                "recent_openings": recent_openings,
                "recent_applications": recent_applications
            }
        }
        
        return SuccessResponse(
            message="팀 매칭 통계 조회에 성공했습니다.",
            data=statistics
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"통계 조회 중 오류: {str(e)}"
        )

@router.get("/recommendations/{user_id}", response_model=SuccessResponse)
async def get_recommended_openings(
    user_id: int,
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """사용자에게 추천하는 팀 모집 공고 (기본적인 추천 로직)"""
    try:
        # 사용자 정보 조회
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
        # 기본 추천 로직: 사용자의 전공과 관련된 프로젝트의 모집 공고
        query = db.query(TeamOpening).join(Project).join(User).filter(
            TeamOpening.status == "OPEN",
            Project.is_active == True,
            Project.is_public == True
        )
        
        # 같은 전공의 프로젝트를 우선 추천
        if user.major:
            same_major_openings = query.filter(User.major == user.major).limit(limit//2).all()
            other_openings = query.filter(User.major != user.major).limit(limit - len(same_major_openings)).all()
            recommended_openings = same_major_openings + other_openings
        else:
            recommended_openings = query.limit(limit).all()
        
        # 추천 이유와 함께 반환
        recommendations = []
        for opening in recommended_openings:
            opening_data = TeamOpeningResponse.from_orm(opening).model_dump()
            opening_data["project_info"] = {
                "name": opening.project.name,
                "service_type": opening.project.service_type,
                "stage": opening.project.stage,
                "owner_name": opening.project.owner.name,
                "owner_major": opening.project.owner.major
            }
            
            # 추천 이유
            reasons = []
            if opening.project.owner.major == user.major:
                reasons.append("같은 전공 출신의 프로젝트")
            if opening.project.service_type in ["APP", "WEB"]:
                reasons.append("인기 서비스 유형")
                
            opening_data["recommendation_reasons"] = reasons
            recommendations.append(opening_data)
        
        return SuccessResponse(
            message=f"{len(recommendations)}개의 추천 모집 공고를 찾았습니다.",
            data=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"추천 조회 중 오류: {str(e)}"
        )