from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.common import SuccessResponse
from app.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=SuccessResponse)
async def create_project(
    project_data: ProjectCreate, 
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """프로젝트 생성"""
    try:
        new_project = Project(
            owner_id=current_user["user_id"],
            name=project_data.name,
            description=project_data.description,
            idea_name=project_data.idea_name,
            service_type=project_data.service_type,
            target_type=project_data.target_type,
            stage="IDEA"
        )
        
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        project_data = {
            "project_id": new_project.project_id,
            "owner_id": new_project.owner_id,
            "name": new_project.name,
            "description": new_project.description,
            "idea_name": new_project.idea_name,
            "service_type": new_project.service_type,
            "target_type": new_project.target_type,
            "stage": new_project.stage,
            "is_active": new_project.is_active,
            "created_at": new_project.created_at
        }
        
        return SuccessResponse(
            message="프로젝트가 성공적으로 생성되었습니다.",
            data=project_data
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로젝트 생성 중 오류: {str(e)}"
        )

@router.get("/", response_model=SuccessResponse)
async def get_my_projects(
    current_user: dict = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """내 프로젝트 목록"""
    try:
        projects = db.query(Project).filter(
            Project.owner_id == current_user["user_id"],
            Project.is_active == True
        ).order_by(Project.created_at.desc()).all()
        
        projects_data = []
        for project in projects:
            project_dict = {
                "project_id": project.project_id,
                "owner_id": project.owner_id,
                "name": project.name,
                "description": project.description,
                "idea_name": project.idea_name,
                "service_type": project.service_type,
                "target_type": project.target_type,
                "stage": project.stage,
                "is_active": project.is_active,
                "created_at": project.created_at
            }
            projects_data.append(project_dict)
        
        return SuccessResponse(
            message="프로젝트 목록을 성공적으로 조회했습니다.",
            data=projects_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"조회 중 오류: {str(e)}"
        )

@router.get("/public", response_model=SuccessResponse)
async def get_public_projects(
    service_type: Optional[str] = Query(None),
    target_type: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    limit: int = Query(20),
    db: Session = Depends(get_db)
):
    """공개 프로젝트 목록 조회"""
    try:
        query = db.query(Project).filter(Project.is_active == True)
        
        if service_type:
            query = query.filter(Project.service_type == service_type)
        if target_type:
            query = query.filter(Project.target_type == target_type)
        if stage:
            query = query.filter(Project.stage == stage)
        
        projects = query.order_by(Project.created_at.desc()).limit(limit).all()
        
        projects_data = []
        for project in projects:
            owner = db.query(User).filter(User.user_id == project.owner_id).first()
            
            project_dict = {
                "project_id": project.project_id,
                "name": project.name,
                "description": project.description,
                "service_type": project.service_type,
                "target_type": project.target_type,
                "stage": project.stage,
                "created_at": project.created_at,
                "owner_name": owner.name if owner else "Unknown",
                "owner_major": owner.major if owner else None
            }
            projects_data.append(project_dict)
        
        return SuccessResponse(
            message="공개 프로젝트 목록을 성공적으로 조회했습니다.",
            data=projects_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공개 프로젝트 조회 중 오류: {str(e)}"
        )

@router.get("/{project_id}", response_model=SuccessResponse)
async def get_project_detail(project_id: int, db: Session = Depends(get_db)):
    """프로젝트 상세 조회"""
    try:
        project = db.query(Project).filter(
            Project.project_id == project_id,
            Project.is_active == True
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )
        
        owner = db.query(User).filter(User.user_id == project.owner_id).first()
        
        project_data = {
            "project_id": project.project_id,
            "owner_id": project.owner_id,
            "name": project.name,
            "description": project.description,
            "idea_name": project.idea_name,
            "service_type": project.service_type,
            "target_type": project.target_type,
            "stage": project.stage,
            "is_active": project.is_active,
            "created_at": project.created_at,
            "owner_info": {
                "name": owner.name if owner else "Unknown",
                "major": owner.major if owner else None,
                "year": owner.year if owner else None
            }
        }
        
        return SuccessResponse(
            message="프로젝트 상세 정보를 성공적으로 조회했습니다.",
            data=project_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로젝트 상세 조회 중 오류: {str(e)}"
        )

@router.put("/{project_id}", response_model=SuccessResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """프로젝트 정보 수정"""
    try:
        project = db.query(Project).filter(
            Project.project_id == project_id,
            Project.is_active == True
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )
        
        if project.owner_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="프로젝트를 수정할 권한이 없습니다."
            )
        
        # 업데이트할 필드만 수정
        if project_update.name is not None:
            project.name = project_update.name
        if project_update.description is not None:
            project.description = project_update.description
        if project_update.stage is not None:
            valid_stages = ["IDEA", "PROTOTYPE", "MVP", "BETA", "LAUNCH"]
            if project_update.stage not in valid_stages:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"유효하지 않은 단계입니다. 가능한 값: {', '.join(valid_stages)}"
                )
            project.stage = project_update.stage
        
        db.commit()
        db.refresh(project)
        
        project_data = {
            "project_id": project.project_id,
            "owner_id": project.owner_id,
            "name": project.name,
            "description": project.description,
            "idea_name": project.idea_name,
            "service_type": project.service_type,
            "target_type": project.target_type,
            "stage": project.stage,
            "is_active": project.is_active,
            "created_at": project.created_at
        }
        
        return SuccessResponse(
            message="프로젝트가 성공적으로 수정되었습니다.",
            data=project_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로젝트 수정 중 오류: {str(e)}"
        )

@router.delete("/{project_id}", response_model=SuccessResponse)
async def delete_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """프로젝트 삭제 (비활성화)"""
    try:
        project = db.query(Project).filter(
            Project.project_id == project_id,
            Project.is_active == True
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="프로젝트를 찾을 수 없습니다."
            )
        
        if project.owner_id != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="프로젝트를 삭제할 권한이 없습니다."
            )
        
        project.is_active = False
        db.commit()
        
        return SuccessResponse(
            message="프로젝트가 성공적으로 삭제되었습니다.",
            data={"project_id": project_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로젝트 삭제 중 오류: {str(e)}"
        )

@router.get("/test")
async def test_projects():
    return {"message": "Projects router working"}