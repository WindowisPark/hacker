# backend/app/routers/research_labs.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
import json

from app.database import get_db
from app.models.research_lab import ResearchLab, Professor, Department, ProjectLabMatching
from app.models.project import Project
from app.schemas.research_lab import (
    ResearchLabResponse, LabSearchRequest, ProjectMatchingRequest, 
    ProjectMatchingResponse, LabMatchingStatusUpdate, ProjectLabMatchingResponse
)
from app.schemas.common import SuccessResponse
from app.auth import get_current_user
from app.services.lab_matching import LabMatchingService

router = APIRouter(tags=["Research Labs"])

@router.get("/", response_model=SuccessResponse)
async def get_research_labs(
    department: Optional[str] = Query(None, description="학과명으로 필터"),
    research_area: Optional[str] = Query(None, description="연구분야로 검색"),
    keyword: Optional[str] = Query(None, description="키워드로 검색"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """연구실 목록 조회 및 검색"""
    try:
        query = db.query(ResearchLab).filter(ResearchLab.is_active == True)
        
        # 학과별 필터링
        if department:
            query = query.join(Professor).join(Department).filter(
                Department.name.ilike(f"%{department}%")
            )
        
        # 연구분야로 검색
        if research_area:
            query = query.filter(
                or_(
                    ResearchLab.research_areas.ilike(f"%{research_area}%"),
                    ResearchLab.keywords.ilike(f"%{research_area}%")
                )
            )
        
        # 키워드로 검색
        if keyword:
            query = query.filter(
                or_(
                    ResearchLab.name.ilike(f"%{keyword}%"),
                    ResearchLab.description.ilike(f"%{keyword}%"),
                    ResearchLab.keywords.ilike(f"%{keyword}%")
                )
            )
        
        labs = query.limit(limit).all()
        
        # 응답 데이터 구성
        labs_data = []
        for lab in labs:
            professor = db.query(Professor).filter(Professor.professor_id == lab.director_id).first()
            department_info = None
            if professor:
                department_info = db.query(Department).filter(Department.department_id == professor.department_id).first()
            
            lab_dict = {
                "lab_id": lab.lab_id,
                "name": lab.name,
                "name_en": lab.name_en,
                "location": lab.location,
                "phone": lab.phone,
                "email": lab.email,
                "website": lab.website,
                "research_areas": json.loads(lab.research_areas) if lab.research_areas else [],
                "keywords": lab.keywords,
                "description": lab.description,
                "tech_stack": json.loads(lab.tech_stack) if lab.tech_stack else [],
                "director_name": professor.name if professor else None,
                "department_name": department_info.name if department_info else None,
                "created_at": lab.created_at.isoformat() if lab.created_at else None,
                "updated_at": lab.updated_at.isoformat() if lab.updated_at else None
            }
            labs_data.append(lab_dict)
        
        return SuccessResponse(
            message=f"{len(labs_data)}개의 연구실을 찾았습니다.",
            data=labs_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"연구실 조회 중 오류: {str(e)}"
        )

@router.get("/{lab_id}", response_model=SuccessResponse)
async def get_research_lab_detail(lab_id: int, db: Session = Depends(get_db)):
    """연구실 상세 정보 조회"""
    try:
        lab = db.query(ResearchLab).filter(
            ResearchLab.lab_id == lab_id,
            ResearchLab.is_active == True
        ).first()
        
        if not lab:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="연구실을 찾을 수 없습니다."
            )
        
        # 교수 및 학과 정보 조회
        professor = db.query(Professor).filter(Professor.professor_id == lab.director_id).first()
        department = None
        if professor:
            department = db.query(Department).filter(Department.department_id == professor.department_id).first()
        
        # 상세 정보 구성
        lab_detail = {
            "lab_id": lab.lab_id,
            "name": lab.name,
            "name_en": lab.name_en,
            "location": lab.location,
            "phone": lab.phone,
            "email": lab.email,
            "website": lab.website,
            "research_areas": json.loads(lab.research_areas) if lab.research_areas else [],
            "keywords": lab.keywords,
            "description": lab.description,
            "tech_stack": json.loads(lab.tech_stack) if lab.tech_stack else [],
            "collaboration_history": json.loads(lab.collaboration_history) if lab.collaboration_history else [],
            "recent_projects": json.loads(lab.recent_projects) if lab.recent_projects else [],
            "director": {
                "name": professor.name if professor else None,
                "position": professor.position if professor else None,
                "email": professor.email if professor else None,
                "office_location": professor.office_location if professor else None,
                "research_fields": professor.research_fields if professor else None
            } if professor else None,
            "department": {
                "name": department.name if department else None,
                "name_en": department.name_en if department else None,
                "college": department.college if department else None,
                "building": department.building if department else None
            } if department else None,
            "created_at": lab.created_at,
            "updated_at": lab.updated_at
        }
        
        return SuccessResponse(
            message="연구실 상세 정보를 성공적으로 조회했습니다.",
            data=lab_detail
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"연구실 상세 조회 중 오류: {str(e)}"
        )

@router.post("/match-project", response_model=SuccessResponse)
async def find_matching_labs_for_project(
    request: ProjectMatchingRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """프로젝트에 적합한 연구실 매칭"""
    try:
        # 프로젝트 소유권 확인
        project = db.query(Project).filter(Project.project_id == request.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )
        
        if project.owner_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="프로젝트 소유자만 연구실 매칭을 요청할 수 있습니다."
            )
        
        # 매칭 서비스 실행
        matching_service = LabMatchingService(db)
        matches = matching_service.find_matching_labs(request)
        
        # 매칭 결과 저장
        matching_service.save_matching_results(request.project_id, matches)
        
        # 응답 구성
        response_data = {
            "project_id": project.project_id,
            "project_name": project.name,
            "project_description": project.description,
            "total_matches": len(matches),
            "matches": matches
        }
        
        return SuccessResponse(
            message=f"{len(matches)}개의 매칭되는 연구실을 찾았습니다.",
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"연구실 매칭 중 오류: {str(e)}"
        )

@router.get("/project/{project_id}/matches", response_model=SuccessResponse)
async def get_project_matching_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """프로젝트의 연구실 매칭 이력 조회"""
    try:
        # 프로젝트 소유권 확인
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )
        
        if project.owner_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="프로젝트 소유자만 매칭 이력을 조회할 수 있습니다."
            )
        
        # 매칭 이력 조회
        matching_service = LabMatchingService(db)
        history = matching_service.get_project_matching_history(project_id)
        
        return SuccessResponse(
            message="매칭 이력을 성공적으로 조회했습니다.",
            data={
                "project_id": project_id,
                "project_name": project.name,
                "matches": history
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"매칭 이력 조회 중 오류: {str(e)}"
        )

@router.put("/matching/{matching_id}/status", response_model=SuccessResponse)
async def update_matching_status(
    matching_id: int,
    status_update: LabMatchingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """매칭 상태 업데이트 (연락함, 관심있음, 거절됨 등)"""
    try:
        # 매칭 레코드 조회
        matching = db.query(ProjectLabMatching).filter(
            ProjectLabMatching.matching_id == matching_id
        ).first()
        
        if not matching:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="매칭 레코드를 찾을 수 없습니다."
            )
        
        # 프로젝트 소유권 확인
        project = db.query(Project).filter(Project.project_id == matching.project_id).first()
        if project.owner_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="프로젝트 소유자만 매칭 상태를 변경할 수 있습니다."
            )
        
        # 상태 업데이트
        valid_statuses = ["SUGGESTED", "CONTACTED", "INTERESTED", "DECLINED", "COLLABORATION"]
        if status_update.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 상태입니다. 가능한 값: {', '.join(valid_statuses)}"
            )
        
        matching.status = status_update.status
        if status_update.status == "CONTACTED":
            matching.contacted_at = db.execute("SELECT datetime('now')").scalar()
        elif status_update.status in ["INTERESTED", "DECLINED"]:
            matching.response_at = db.execute("SELECT datetime('now')").scalar()
        
        # 메모가 있으면 매칭 이유에 추가
        if status_update.notes:
            current_reason = matching.matching_reason or ""
            matching.matching_reason = f"{current_reason}\n\n사용자 메모: {status_update.notes}"
        
        db.commit()
        
        return SuccessResponse(
            message="매칭 상태가 성공적으로 업데이트되었습니다.",
            data={
                "matching_id": matching_id,
                "new_status": matching.status,
                "updated_at": matching.response_at or matching.contacted_at
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"매칭 상태 업데이트 중 오류: {str(e)}"
        )

@router.get("/departments")
async def get_departments(db: Session = Depends(get_db)):
    """학과 목록 조회"""
    try:
        departments = db.query(Department).all()
        
        dept_data = []
        for dept in departments:
            # 각 학과의 연구실 수 계산
            lab_count = db.query(ResearchLab).join(Professor).filter(
                Professor.department_id == dept.department_id,
                ResearchLab.is_active == True
            ).count()
            
            dept_dict = {
                "department_id": dept.department_id,
                "name": dept.name,
                "name_en": dept.name_en,
                "college": dept.college,
                "building": dept.building,
                "description": dept.description,
                "lab_count": lab_count,
                "created_at": dept.created_at.isoformat() if dept.created_at else None
            }
            dept_data.append(dept_dict)
        
        return {
            "success": True,
            "message": "학과 목록을 성공적으로 조회했습니다.",
            "data": dept_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"학과 목록 조회 중 오류: {str(e)}"
        )

@router.get("/statistics")
async def get_lab_statistics(db: Session = Depends(get_db)):
    """연구실 관련 통계"""
    try:
        # 기본 통계
        total_labs = db.query(ResearchLab).filter(ResearchLab.is_active == True).count()
        total_departments = db.query(Department).count()
        total_professors = db.query(Professor).filter(Professor.is_active == True).count()
        
        # 학과별 연구실 수
        dept_stats = db.execute("""
            SELECT d.name, COUNT(rl.lab_id) as lab_count
            FROM departments d
            LEFT JOIN professors p ON d.department_id = p.department_id
            LEFT JOIN research_labs rl ON p.professor_id = rl.director_id AND rl.is_active = 1
            GROUP BY d.department_id, d.name
            ORDER BY lab_count DESC
        """).fetchall()
        
        dept_distribution = {row[0]: row[1] for row in dept_stats}
        
        # 최근 매칭 활동
        recent_matchings = db.query(ProjectLabMatching).filter(
            ProjectLabMatching.created_at >= db.execute("SELECT datetime('now', '-30 days')").scalar()
        ).count()
        
        # 매칭 상태별 분포
        status_stats = db.execute("""
            SELECT status, COUNT(*) as count
            FROM project_lab_matchings
            GROUP BY status
        """).fetchall()
        
        status_distribution = {row[0]: row[1] for row in status_stats}
        
        statistics = {
            "overview": {
                "total_labs": total_labs,
                "total_departments": total_departments,
                "total_professors": total_professors,
                "recent_matchings": recent_matchings
            },
            "department_distribution": dept_distribution,
            "matching_status_distribution": status_distribution
        }
        
        return {
            "success": True,
            "message": "연구실 통계를 성공적으로 조회했습니다.",
            "data": statistics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"통계 조회 중 오류: {str(e)}"
        )

@router.get("/recommendations/{project_id}", response_model=SuccessResponse)
async def get_recommended_labs(
    project_id: int,
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """프로젝트에 추천하는 연구실 (간단한 추천)"""
    try:
        # 프로젝트 조회 및 권한 확인
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )
        
        if project.owner_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="프로젝트 소유자만 추천을 받을 수 있습니다."
            )
        
        # 기본 매칭 요청 생성
        matching_request = ProjectMatchingRequest(
            project_id=project_id,
            max_results=limit,
            min_score=0.2  # 낮은 임계값으로 더 많은 결과 포함
        )
        
        # 매칭 서비스 실행
        matching_service = LabMatchingService(db)
        recommendations = matching_service.find_matching_labs(matching_request)
        
        # 추천 이유 간소화
        simplified_recommendations = []
        for rec in recommendations:
            simplified = {
                "lab_id": rec["lab_id"],
                "lab_name": rec["lab_name"],
                "director_name": rec["director_name"],
                "department_name": rec["department_name"],
                "similarity_score": rec["similarity_score"],
                "research_areas": json.loads(rec["research_areas"]) if rec["research_areas"] else [],
                "recommendation_reason": f"유사도 {rec['similarity_score']:.1%} - 연구분야 및 기술스택 매칭",
                "contact_info": rec["contact_info"]
            }
            simplified_recommendations.append(simplified)
        
        return SuccessResponse(
            message=f"{len(simplified_recommendations)}개의 추천 연구실을 찾았습니다.",
            data={
                "project_name": project.name,
                "recommendations": simplified_recommendations
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"연구실 추천 중 오류: {str(e)}"
        )