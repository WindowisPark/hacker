import json
import time
import random
import socket
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.ai_report import AIReport
from app.models.project import Project
from app.schemas.ai_report import AIReportRequest, AIReportResponse, AIReportStatus, AIReportFeedback
from app.schemas.common import SuccessResponse
from app.auth import get_current_user

# --- AI 서비스 TCP 서버 설정 ---
# AI 개발자의 PC가 실행할 서버의 IP 주소와 포트 번호입니다.
# 테스트 시에는 '127.0.0.1'(localhost), 실제 협업 시에는 AI 개발자 PC의 로컬 IP 주소(예: "192.168.0.5")를 입력하세요.
AI_SERVICE_HOST = "127.0.0.1"
AI_SERVICE_PORT = 9999

def request_report_via_tcp(request_data: AIReportRequest) -> dict:
    """
    TCP 통신을 통해 별도의 AI 서비스에 아이디어 분석을 요청하고 결과를 받아옵니다.
    """
    # 전송할 데이터를 JSON 형식으로 직렬화
    payload = request_data.model_dump_json()

    try:
        # TCP 클라이언트 소켓 생성 및 서버에 연결
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # 타임아웃 설정 (예: 60초)
            client_socket.settimeout(60.0)
            client_socket.connect((AI_SERVICE_HOST, AI_SERVICE_PORT))
            
            # AI 서비스에 데이터 전송
            client_socket.sendall(payload.encode('utf-8'))
            
            # AI 서비스로부터 결과 수신
            buffer = b""
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                buffer += data
            
            # 수신된 데이터를 JSON으로 파싱하여 반환
            if not buffer:
                raise Exception("AI 서비스로부터 빈 응답을 받았습니다.")
                
            response_json = json.loads(buffer.decode('utf-8'))
            return response_json

    except socket.timeout:
        # 타임아웃 예외 처리
        raise Exception(f"AI 서비스({AI_SERVICE_HOST}:{AI_SERVICE_PORT}) 연결 시간 초과")
    except socket.error as e:
        # 네트워크 관련 예외 처리
        raise Exception(f"AI 서비스({AI_SERVICE_HOST}:{AI_SERVICE_PORT})와 통신 중 오류 발생: {e}")
    except json.JSONDecodeError:
        # JSON 파싱 예외 처리
        raise Exception("AI 서비스로부터 받은 응답의 형식이 올바르지 않습니다.")


router = APIRouter(tags=["AI Reports"])


def generate_report_background(report_id: int, request_data: AIReportRequest, db: Session):
    """
    백그라운드에서 실행될 AI 리포트 생성 함수
    """
    start_time = time.time()
    report = None
    try:
        report = db.query(AIReport).filter(AIReport.report_id == report_id).first()
        if not report:
            print(f"Error: Report ID {report_id} not found in DB.")
            return

        # TCP 통신으로 AI 서비스에 분석 요청
        llm_result = request_report_via_tcp(request_data)

        # 분석 결과를 JSON 문자열로 변환하여 DB에 업데이트
        report.idea_info = json.dumps(llm_result.get("idea_info", {}), ensure_ascii=False)
        report.existing_services = json.dumps(llm_result.get("existing_services", {}), ensure_ascii=False)
        report.service_limitations = json.dumps(llm_result.get("service_limitations", {}), ensure_ascii=False)
        report.lean_canvas_detailed = json.dumps(llm_result.get("lean_canvas_detailed", {}), ensure_ascii=False)

        # 메타데이터 업데이트
        end_time = time.time()
        report.generation_time_seconds = int(end_time - start_time)
        report.status = "COMPLETED"
        # 실제 AI 서비스 결과에 따라 confidence_score, token_usage 등을 받아올 수 있습니다.
        report.confidence_score = llm_result.get("metadata", {}).get("confidence_score", round(random.uniform(0.75, 0.98), 2))
        report.token_usage = llm_result.get("metadata", {}).get("token_usage", random.randint(1500, 3000))
        
        db.commit()

    except Exception as e:
        if report:
            report.status = "FAILED"
            report.error_message = str(e)
            db.commit()
        print(f"Error generating report {report_id}: {e}")
    finally:
        db.close()


@router.post("/", status_code=status.HTTP_202_ACCEPTED, response_model=AIReportStatus)
async def create_ai_report(
    request: AIReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    AI 분석 보고서 생성을 요청하고 백그라운드 작업을 시작합니다.
    """
    project = db.query(Project).filter(Project.project_id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="해당 프로젝트를 찾을 수 없습니다.")
    if project.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="프로젝트 소유자만 보고서를 생성할 수 있습니다.")

    new_report = AIReport(
        project_id=request.project_id,
        requester_id=current_user["user_id"],
        report_type="LEAN_CANVAS",
        status="GENERATING",
        error_message=None
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    background_tasks.add_task(generate_report_background, new_report.report_id, request, next(get_db()))

    return AIReportStatus(
        report_id=new_report.report_id,
        status="GENERATING",
        progress_percentage=0,
        estimated_time=60 # 예상 소요시간 (초)
    )

@router.get("/{report_id}/status", response_model=AIReportStatus)
async def get_report_status(report_id: int, db: Session = Depends(get_db)):
    """
    AI 보고서의 현재 생성 상태를 확인합니다.
    """
    report = db.query(AIReport).filter(AIReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="해당 보고서를 찾을 수 없습니다.")
    
    progress = 0
    if report.status == "GENERATING":
        # 실제로는 단계별 진행률을 DB에 기록하여 가져올 수 있습니다.
        progress = random.randint(10, 90)
    elif report.status == "COMPLETED":
        progress = 100

    return AIReportStatus(
        report_id=report.report_id,
        status=report.status,
        progress_percentage=progress,
        error_message=report.error_message
    )

@router.get("/{report_id}", response_model=SuccessResponse)
async def get_ai_report(report_id: int, db: Session = Depends(get_db)):
    """
    완성된 AI 분석 보고서의 상세 내용을 조회합니다.
    """
    report = db.query(AIReport).filter(AIReport.report_id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="해당 보고서를 찾을 수 없습니다.")
    if report.status != "COMPLETED":
        raise HTTPException(status_code=400, detail=f"보고서가 아직 생성 중이거나 실패했습니다. (상태: {report.status})")

    # DB에 저장된 JSON 문자열을 Python 딕셔너리로 변환
    # JSON 파싱 오류 방지를 위해 기본값 {} 제공
    try:
        idea_info_data = json.loads(report.idea_info) if report.idea_info else {}
        existing_services_data = json.loads(report.existing_services) if report.existing_services else {}
        service_limitations_data = json.loads(report.service_limitations) if report.service_limitations else {}
        lean_canvas_detailed_data = json.loads(report.lean_canvas_detailed) if report.lean_canvas_detailed else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="보고서 데이터 형식이 올바르지 않습니다.")

    response_payload = AIReportResponse(
        report_id=report.report_id,
        project_id=report.project_id,
        requester_id=report.requester_id,
        report_type=report.report_type,
        idea_info=idea_info_data,
        existing_services=existing_services_data,
        service_limitations=service_limitations_data,
        lean_canvas_detailed=lean_canvas_detailed_data,
        confidence_score=report.confidence_score,
        data_sources=report.data_sources,
        generation_time_seconds=report.generation_time_seconds,
        token_usage=report.token_usage,
        created_at=report.created_at,
        is_latest=report.is_latest,
        user_feedback_rating=report.user_feedback_rating,
        user_feedback_comment=report.user_feedback_comment
    )

    return SuccessResponse(message="보고서 조회가 완료되었습니다.", data=response_payload.model_dump())

@router.post("/{report_id}/feedback", response_model=SuccessResponse)
async def submit_feedback(
    report_id: int, 
    feedback: AIReportFeedback,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    생성된 보고서에 대한 사용자 피드백을 제출합니다.
    """
    report = db.query(AIReport).filter(AIReport.report_id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="해당 보고서를 찾을 수 없습니다.")
    if report.requester_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="보고서 요청자만 피드백을 남길 수 있습니다.")
    if not (1 <= feedback.rating <= 5):
        raise HTTPException(status_code=400, detail="평점은 1에서 5 사이여야 합니다.")

    report.user_feedback_rating = feedback.rating
    report.user_feedback_comment = feedback.comment
    db.commit()

    return SuccessResponse(message="피드백이 성공적으로 제출되었습니다.")

@router.get("/project/{project_id}", response_model=SuccessResponse)
async def get_reports_for_project(project_id: int, db: Session = Depends(get_db)):
    """
    특정 프로젝트에 속한 모든 AI 보고서 목록을 조회합니다.
    """
    reports = db.query(AIReport).filter(AIReport.project_id == project_id).order_by(AIReport.created_at.desc()).all()
    
    if not reports:
        return SuccessResponse(message="해당 프로젝트에 대한 보고서가 없습니다.", data=[])

    # Pydantic 모델을 사용하여 응답 데이터 구조화 (간단한 정보만 포함)
    reports_data = [
        {
            "report_id": r.report_id,
            "report_type": r.report_type,
            "status": r.status,
            "created_at": r.created_at,
            "confidence_score": r.confidence_score,
            "user_feedback_rating": r.user_feedback_rating
        } for r in reports
    ]
    
    return SuccessResponse(message="프로젝트의 보고서 목록입니다.", data=reports_data)