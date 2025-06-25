from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lean_canvas import LeanCanvas
from app.models.project import Project
from app.schemas.lean_canvas import LeanCanvasUpdate, LeanCanvasResponse
from app.schemas.common import SuccessResponse
from app.auth import get_current_user

# prefix는 main.py에서 설정하므로 여기서는 제외합니다.
router = APIRouter(tags=["lean-canvas"])

@router.get("/project/{project_id}", response_model=SuccessResponse)
async def get_lean_canvas(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    특정 프로젝트에 연결된 린 캔버스의 내용을 조회합니다.
    """
    # 1. 프로젝트가 존재하는지, 그리고 요청한 사용자가 소유자인지 확인
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    if project.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="프로젝트 소유자만 린 캔버스를 조회할 수 있습니다.")

    # 2. 프로젝트 ID로 린 캔버스 조회
    canvas = db.query(LeanCanvas).filter(LeanCanvas.project_id == project_id).first()

    if not canvas:
        raise HTTPException(status_code=404, detail="해당 프로젝트에 생성된 린 캔버스가 없습니다.")

    # 3. LeanCanvasResponse 스키마에 맞춰 데이터 반환
    return SuccessResponse(
        message="린 캔버스를 성공적으로 조회했습니다.",
        data=LeanCanvasResponse.from_orm(canvas)
    )

@router.put("/project/{project_id}", response_model=SuccessResponse)
async def create_or_update_lean_canvas(
    project_id: int,
    canvas_data: LeanCanvasUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    프로젝트의 린 캔버스 내용을 생성하거나 수정하여 저장합니다 (Upsert).
    """
    # 1. 프로젝트 존재 및 소유권 확인
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    if project.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="프로젝트 소유자만 린 캔버스를 수정할 수 있습니다.")

    # 2. 기존 린 캔버스가 있는지 확인
    canvas = db.query(LeanCanvas).filter(LeanCanvas.project_id == project_id).first()

    # Pydantic 모델을 딕셔너리로 변환하되, 사용자가 명시적으로 전달한 값만 포함
    update_data = canvas_data.model_dump(exclude_unset=True)

    if canvas:
        # 3-1. 캔버스가 존재하면 -> 업데이트
        for key, value in update_data.items():
            setattr(canvas, key, value)
        canvas.canvas_version += 1 # 버전 정보 업데이트
    else:
        # 3-2. 캔버스가 없으면 -> 새로 생성
        new_canvas_data = update_data
        new_canvas_data['project_id'] = project_id
        canvas = LeanCanvas(**new_canvas_data)
        db.add(canvas)

    try:
        db.commit()
        db.refresh(canvas)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"데이터베이스 저장 중 오류가 발생했습니다: {str(e)}")

    # 4. 저장된 결과를 LeanCanvasResponse 스키마에 맞춰 반환
    return SuccessResponse(
        message="린 캔버스가 성공적으로 저장되었습니다.",
        data=LeanCanvasResponse.from_orm(canvas)
    )
