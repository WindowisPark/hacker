# backend/app/routers/ai_reports.py (AI 서버 필드명에 맞춘 매핑)

import requests
import json
import time
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.ai_report import AIReport
from app.models.project import Project
from app.schemas.ai_report import AIReportRequest, AIReportResponse, AIReportStatus, AIReportFeedback
from app.schemas.common import SuccessResponse
from app.auth import get_current_user

# AI 서버 HTTP 설정
AI_SERVICE_HOST = "172.16.50.121"
AI_SERVICE_PORT = 9999
AI_SERVICE_URL = f"http://{AI_SERVICE_HOST}:{AI_SERVICE_PORT}"

def map_project_to_ai_request(project: Project, request: AIReportRequest) -> dict:
    """
    프로젝트 정보를 AI 서버가 기대하는 형태로 매핑
    AI 서버 필드: subject, specific, deploy_method, service_target
    """
    # subject: 서비스의 주제 (예: "학습 서비스")
    subject = request.industry if request.industry else extract_subject_from_description(project.description, project.name)
    
    # specific: 구체적인 서비스 내용 (예: "PDF 요약 에이전트 서비스")
    specific = request.idea_description or project.description
    
    # deploy_method: 배포 방식 (예: "Web", "App")
    deploy_method = map_service_type_to_deploy_method(project.service_type)
    
    # service_target: 서비스 대상 (예: "B2C", "B2B")
    service_target = project.target_type or "B2C"
    
    return {
        "subject": subject,
        "specific": specific, 
        "deploy_method": deploy_method,
        "service_target": service_target
    }

def extract_subject_from_description(description: str, name: str) -> str:
    """
    프로젝트 설명이나 이름에서 주제를 추출
    """
    # 일반적인 서비스 카테고리 키워드
    categories = {
        "학습": ["학습", "교육", "공부", "스터디", "강의", "수업"],
        "쇼핑": ["쇼핑", "구매", "판매", "마켓", "커머스", "중고"],
        "소셜": ["소셜", "커뮤니티", "채팅", "만남", "친구"],
        "음식": ["음식", "배달", "요리", "맛집", "레스토랑"],
        "건강": ["건강", "운동", "헬스", "다이어트", "의료"],
        "금융": ["금융", "결제", "송금", "투자", "대출"],
        "여행": ["여행", "숙박", "예약", "관광"],
        "업무": ["업무", "협업", "프로젝트", "관리", "자동화"]
    }
    
    text = (description + " " + name).lower()
    
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return f"{category} 서비스"
    
    # 키워드 매칭이 안되면 프로젝트 이름의 첫 번째 단어 사용
    return name.split()[0] if name else "일반 서비스"

def map_service_type_to_deploy_method(service_type: str) -> str:
    """
    프로젝트의 service_type을 AI 서비스가 기대하는 deploy_method로 변환
    """
    mapping = {
        "APP": "App",
        "WEB": "Web", 
        "AI": "Web",
        "ETC": "Web"
    }
    return mapping.get(service_type, "Web")

def request_report_via_http(ai_request_data: dict) -> dict:
    """
    HTTP 통신을 통해 AI 서비스에 비즈니스 보고서 생성을 요청
    """
    try:
        print(f"[DEBUG] AI 서버 요청 데이터: {ai_request_data}")
        
        response = requests.post(
            f"{AI_SERVICE_URL}/generate-report",
            json=ai_request_data,
            headers={"Content-Type": "application/json"},
            timeout=180  # 3분 타임아웃
        )
        
        print(f"[DEBUG] AI 서버 응답 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"[DEBUG] AI 서버 응답 성공: {type(result)}")
            return result
        else:
            error_msg = f"AI 서버 HTTP 오류: {response.status_code} - {response.text}"
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg)
            
    except requests.exceptions.Timeout:
        raise Exception("AI 서버 응답 시간 초과 (3분)")
    except requests.exceptions.ConnectionError:
        raise Exception(f"AI 서버에 연결할 수 없습니다: {AI_SERVICE_URL}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP 요청 중 오류: {str(e)}")
    except Exception as e:
        raise Exception(f"AI 보고서 생성 중 오류: {str(e)}")

router = APIRouter(tags=["AI Reports"])

def generate_report_background(report_id: int, ai_request_data: dict, db: Session):
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

        print(f"[DEBUG] 백그라운드 AI 보고서 생성 시작")

        # HTTP 통신으로 AI 서비스에 보고서 생성 요청
        llm_result = request_report_via_http(ai_request_data)

        print(f"[DEBUG] AI 서비스 응답 받음: {type(llm_result)}")

        # AI 서비스의 응답 구조에 맞게 파싱
        if isinstance(llm_result, dict):
            # AI 서비스가 반환하는 구조에 맞게 파싱
            existing_services = llm_result.get("existing_services", {})
            lean_canvas = llm_result.get("lean_canvas", {})
            service_limitations = llm_result.get("service_limitations", {})
            
            # 아이디어 정보 (요청 데이터 포함)
            idea_info = {
                "subject": ai_request_data.get("subject"),
                "specific": ai_request_data.get("specific"),
                "deploy_method": ai_request_data.get("deploy_method"),
                "service_target": ai_request_data.get("service_target"),
                "ai_analysis": llm_result
            }
        else:
            # 응답이 예상과 다른 형태인 경우
            existing_services = {"analysis": "AI 서비스 응답 파싱 오류"}
            lean_canvas = {"error": "데이터 파싱 실패"}
            service_limitations = {"note": "응답 형식 확인 필요"}
            idea_info = ai_request_data

        # DB 업데이트
        report.idea_info = json.dumps(idea_info, ensure_ascii=False)
        report.existing_services = json.dumps(existing_services, ensure_ascii=False)
        report.service_limitations = json.dumps(service_limitations, ensure_ascii=False)
        report.lean_canvas_detailed = json.dumps(lean_canvas, ensure_ascii=False)

        # 메타데이터 업데이트
        end_time = time.time()
        report.generation_time_seconds = int(end_time - start_time)
        report.status = "COMPLETED"
        
        # 신뢰도 점수와 토큰 사용량
        metadata = llm_result.get("metadata", {}) if isinstance(llm_result, dict) else {}
        report.confidence_score = metadata.get("confidence_score", 0.85)
        report.token_usage = metadata.get("token_usage", 2000)
        
        db.commit()
        print(f"[DEBUG] 백그라운드 보고서 생성 완료: {report.report_id}")

    except Exception as e:
        print(f"[ERROR] 백그라운드 보고서 생성 오류: {e}")
        if report:
            report.status = "FAILED"
            report.error_message = str(e)
            db.commit()
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
    오직 본인 소유의 프로젝트에 대해서만 보고서 생성 가능합니다.
    """
    
    # 1. 프로젝트 존재 여부 및 소유권 확인
    project = db.query(Project).filter(
        Project.project_id == request.project_id,
        Project.owner_id == current_user["user_id"],  # 본인 프로젝트만
        Project.is_active == True  # 활성 프로젝트만
    ).first()
    
    if not project:
        print(f"[SECURITY] 사용자 {current_user['user_id']}가 프로젝트 {request.project_id}에 접근 시도")
        raise HTTPException(
            status_code=404, 
            detail="해당 프로젝트를 찾을 수 없거나 접근 권한이 없습니다."
        )
    
    print(f"[DEBUG] 권한 확인 완료: 사용자 {current_user['user_id']} → 프로젝트 {project.project_id} ({project.name})")

    # 2. 이미 생성 중인 보고서가 있는지 확인 (중복 방지)
    existing_report = db.query(AIReport).filter(
        AIReport.project_id == request.project_id,
        AIReport.status == "GENERATING"
    ).first()
    
    if existing_report:
        return AIReportStatus(
            report_id=existing_report.report_id,
            status="GENERATING",
            progress_percentage=50,  # 이미 진행 중
            estimated_time=120
        )

    # 3. 프로젝트 정보를 AI 서버 요청 형태로 매핑
    ai_request_data = map_project_to_ai_request(project, request)
    
    print(f"[DEBUG] 매핑된 AI 요청 데이터: {ai_request_data}")

    # 4. AI 보고서 레코드 생성
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

    print(f"[DEBUG] AI 보고서 생성 시작: Report ID {new_report.report_id}")

    # 5. 백그라운드 작업 시작
    background_tasks.add_task(generate_report_background, new_report.report_id, ai_request_data, next(get_db()))

    return AIReportStatus(
        report_id=new_report.report_id,
        status="GENERATING",
        progress_percentage=0,
        estimated_time=180
    )

# 또는 더 간단한 방법: 프로젝트 ID 없이 직접 프로젝트 정보 전달
@router.post("/create-direct", status_code=status.HTTP_202_ACCEPTED, response_model=AIReportStatus)
async def create_ai_report_direct_input(
    project_info: dict,  # 프로젝트 정보를 직접 전달
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    프로젝트 정보를 직접 입력받아 AI 보고서를 생성합니다.
    프로젝트 ID 없이 바로 정보를 받아서 처리하므로 더 안전합니다.
    
    요청 예시:
    {
        "project_name": "스마트 러닝 도우미",
        "description": "AI 기반 개인 맞춤 학습 서비스",
        "industry": "교육기술",
        "service_type": "WEB",
        "target_type": "B2C",
        "idea_description": "개인화된 학습 경로 제공"
    }
    """
    
    try:
        # 1. 필수 정보 검증
        required_fields = ["project_name", "description", "service_type", "target_type"]
        missing_fields = [field for field in required_fields if not project_info.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"필수 정보가 누락되었습니다: {', '.join(missing_fields)}"
            )

        # 2. AI 서버 요청 데이터 직접 구성
        ai_request_data = {
            "subject": project_info.get("industry", "일반 서비스"),
            "specific": project_info.get("idea_description", project_info["description"]),
            "deploy_method": map_service_type_to_deploy_method(project_info["service_type"]),
            "service_target": project_info["target_type"]
        }
        
        print(f"[DEBUG] 직접 입력 AI 요청 데이터: {ai_request_data}")

        # 3. 임시 프로젝트 생성 (선택사항 - 보고서만 필요하면 생략 가능)
        temp_project = Project(
            owner_id=current_user["user_id"],
            name=project_info["project_name"],
            description=project_info["description"],
            service_type=project_info["service_type"],
            target_type=project_info["target_type"],
            stage="IDEA",
            is_public=False  # 임시 프로젝트는 비공개
        )
        db.add(temp_project)
        db.commit()
        db.refresh(temp_project)

        # 4. AI 보고서 레코드 생성
        new_report = AIReport(
            project_id=temp_project.project_id,
            requester_id=current_user["user_id"],
            report_type="LEAN_CANVAS",
            status="GENERATING",
            error_message=None
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)

        # 5. 백그라운드 작업 시작
        background_tasks.add_task(generate_report_background, new_report.report_id, ai_request_data, next(get_db()))

        return AIReportStatus(
            report_id=new_report.report_id,
            status="GENERATING",
            progress_percentage=0,
            estimated_time=180
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 직접 입력 보고서 생성 오류: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="보고서 생성 중 오류가 발생했습니다."
        )

# 내 프로젝트 목록 조회 (보고서 생성용)
@router.get("/my-projects", response_model=SuccessResponse)
async def get_my_projects_for_report(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI 보고서 생성을 위한 내 프로젝트 목록 조회
    """
    try:
        projects = db.query(Project).filter(
            Project.owner_id == current_user["user_id"],
            Project.is_active == True
        ).order_by(Project.created_at.desc()).all()
        
        projects_data = []
        for project in projects:
            # 해당 프로젝트의 보고서 생성 이력 확인
            report_count = db.query(AIReport).filter(
                AIReport.project_id == project.project_id
            ).count()
            
            latest_report = db.query(AIReport).filter(
                AIReport.project_id == project.project_id
            ).order_by(AIReport.created_at.desc()).first()
            
            project_dict = {
                "project_id": project.project_id,
                "name": project.name,
                "description": project.description,
                "service_type": project.service_type,
                "target_type": project.target_type,
                "stage": project.stage,
                "created_at": project.created_at,
                "report_count": report_count,
                "latest_report_status": latest_report.status if latest_report else None,
                "can_generate_report": True  # 본인 프로젝트이므로 항상 가능
            }
            projects_data.append(project_dict)
        
        return SuccessResponse(
            message=f"AI 보고서 생성 가능한 프로젝트 {len(projects_data)}개를 조회했습니다.",
            data=projects_data
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프로젝트 목록 조회 중 오류: {str(e)}"
        )

@router.post("/test", response_model=dict)
async def test_ai_report():
    """
    AI 서버 테스트용 엔드포인트 (매핑된 데이터로 테스트)
    """
    test_data = {
        "subject": "학습 서비스",  # AI가 기대하는 형태
        "specific": "PDF 요약 AI Agent - 대학생들이 긴 PDF 자료를 빠르게 요약하여 학습 효율을 높이는 서비스",
        "deploy_method": "Web",
        "service_target": "B2C"
    }
    
    try:
        print(f"[DEBUG] AI 서버 테스트 시작: {test_data}")
        start_time = time.time()
        
        # HTTP 요청
        result = request_report_via_http(test_data)
        generation_time = time.time() - start_time
        
        return {
            "status": "success",
            "message": f"AI 서버 테스트 성공 (응답시간: {generation_time:.1f}초)",
            "test_request": test_data,
            "ai_response": result,
            "response_time_seconds": generation_time,
            "ai_server": f"{AI_SERVICE_URL}/generate-report"
        }
        
    except Exception as e:
        print(f"[ERROR] AI 서버 테스트 실패: {e}")
        return {
            "status": "failed",
            "message": f"AI 서버 테스트 실패: {str(e)}",
            "test_request": test_data,
            "ai_server": f"{AI_SERVICE_URL}/generate-report",
            "error_details": str(e)
        }

@router.post("/test-mapping", response_model=dict)
async def test_project_mapping():
    """
    프로젝트 정보 → AI 서버 형태 매핑 테스트
    """
    # 샘플 프로젝트 정보
    sample_project_data = {
        "name": "스마트 러닝 도우미",
        "description": "개인 맞춤형 AI 학습 계획 및 진도 관리 서비스",
        "service_type": "WEB",
        "target_type": "B2C"
    }
    
    sample_request_data = {
        "industry": "교육기술",
        "idea_description": "AI 기반 개인화 학습 플랫폼으로 학생의 학습 패턴을 분석하여 최적의 학습 계획을 제공"
    }
    
    # 가상의 Project 객체 생성
    class MockProject:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    # 가상의 AIReportRequest 객체 생성
    class MockRequest:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    mock_project = MockProject(**sample_project_data)
    mock_request = MockRequest(**sample_request_data)
    
    # 매핑 테스트
    mapped_data = map_project_to_ai_request(mock_project, mock_request)
    
    return {
        "message": "프로젝트 → AI 서버 매핑 테스트",
        "original_project": sample_project_data,
        "original_request": sample_request_data,
        "mapped_for_ai": mapped_data,
        "mapping_rules": {
            "subject": "industry 또는 프로젝트 설명에서 추출",
            "specific": "idea_description 또는 프로젝트 description",
            "deploy_method": "service_type 변환 (APP→App, WEB→Web)",
            "service_target": "target_type 그대로 사용"
        }
    }

# 1. 보고서 상태 확인
@router.get("/{report_id}/status", response_model=AIReportStatus)
async def get_report_status(report_id: int, db: Session = Depends(get_db)):
    """
    AI 보고서의 현재 생성 상태를 확인합니다.
    
    사용법: GET /ai-reports/3/status
    응답:
    {
        "report_id": 3,
        "status": "COMPLETED",  # GENERATING, COMPLETED, FAILED
        "progress_percentage": 100,
        "error_message": null
    }
    """
    report = db.query(AIReport).filter(AIReport.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="해당 보고서를 찾을 수 없습니다.")
    
    progress = 0
    if report.status == "GENERATING":
        progress = random.randint(10, 90)
    elif report.status == "COMPLETED":
        progress = 100

    return AIReportStatus(
        report_id=report.report_id,
        status=report.status,
        progress_percentage=progress,
        error_message=report.error_message
    )

# 2. 완성된 보고서 상세 조회
@router.get("/{report_id}", response_model=SuccessResponse)
async def get_ai_report(report_id: int, db: Session = Depends(get_db)):
    """
    완성된 AI 분석 보고서의 상세 내용을 조회합니다.
    
    사용법: GET /ai-reports/3
    응답:
    {
        "success": true,
        "message": "보고서 조회가 완료되었습니다.",
        "data": {
            "report_id": 3,
            "project_id": 4,
            "report_type": "LEAN_CANVAS",
            "idea_info": { "subject": "...", "specific": "..." },
            "existing_services": { "analysis": "...", "competitors": [...] },
            "service_limitations": { "technical": "...", "market": "..." },
            "lean_canvas_detailed": { "problem": "...", "solution": "..." },
            "confidence_score": 0.85,
            "generation_time_seconds": 45,
            "created_at": "2024-06-26T..."
        }
    }
    """
    report = db.query(AIReport).filter(AIReport.report_id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="해당 보고서를 찾을 수 없습니다.")
    if report.status != "COMPLETED":
        raise HTTPException(status_code=400, detail=f"보고서가 아직 생성 중이거나 실패했습니다. (상태: {report.status})")

    # DB에 저장된 JSON 문자열을 Python 딕셔너리로 변환
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

# 3. 프로젝트별 보고서 목록 조회
@router.get("/project/{project_id}", response_model=SuccessResponse)
async def get_reports_for_project(project_id: int, db: Session = Depends(get_db)):
    """
    특정 프로젝트에 속한 모든 AI 보고서 목록을 조회합니다.
    
    사용법: GET /ai-reports/project/4
    응답:
    {
        "success": true,
        "message": "프로젝트의 보고서 목록입니다.",
        "data": [
            {
                "report_id": 3,
                "report_type": "LEAN_CANVAS",
                "status": "COMPLETED",
                "created_at": "2024-06-26T...",
                "confidence_score": 0.85,
                "user_feedback_rating": null
            }
        ]
    }
    """
    reports = db.query(AIReport).filter(AIReport.project_id == project_id).order_by(AIReport.created_at.desc()).all()
    
    if not reports:
        return SuccessResponse(message="해당 프로젝트에 대한 보고서가 없습니다.", data=[])

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