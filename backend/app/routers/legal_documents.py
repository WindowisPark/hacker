# backend/app/routers/legal_documents.py
import json
import time
import socket
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project import Project
from app.schemas.legal_documents import (
    LegalDocumentRequest, LegalDocumentResponse, LegalDocumentMarkdown, TemplateInfo
)
from app.schemas.common import SuccessResponse
from app.auth import get_current_user

# --- AI 서비스 TCP 서버 설정 (법적 문서 생성용) ---
AI_LEGAL_SERVICE_HOST = "127.0.0.1"
AI_LEGAL_SERVICE_PORT = 9998

def request_legal_document_via_tcp(request_data: LegalDocumentRequest) -> dict:
    """
    TCP 통신을 통해 AI 서비스에 법적 문서 생성을 요청하고 결과를 받아옵니다.
    """
    payload = request_data.model_dump_json()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.settimeout(60.0)  # 60초 타임아웃
            client_socket.connect((AI_LEGAL_SERVICE_HOST, AI_LEGAL_SERVICE_PORT))
            
            # AI 서비스에 데이터 전송
            client_socket.sendall(payload.encode('utf-8'))
            
            # AI 서비스로부터 결과 수신
            buffer = b""
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                buffer += data
            
            if not buffer:
                raise Exception("AI 법적 문서 서비스로부터 빈 응답을 받았습니다.")
                
            response_json = json.loads(buffer.decode('utf-8'))
            return response_json

    except socket.timeout:
        raise Exception(f"AI 법적 문서 서비스 연결 시간 초과 ({AI_LEGAL_SERVICE_HOST}:{AI_LEGAL_SERVICE_PORT})")
    except socket.error as e:
        raise Exception(f"AI 법적 문서 서비스 통신 오류: {e}")
    except json.JSONDecodeError:
        raise Exception("AI 서비스 응답 형식 오류")


router = APIRouter(tags=["Legal Documents"])


@router.post("/generate", response_model=SuccessResponse)
async def generate_legal_documents(
    request: LegalDocumentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    서비스 이용약관과 개인정보처리방침을 즉시 생성합니다.
    """
    start_time = time.time()
    
    try:
        print(f"[DEBUG] 법적 문서 생성 요청: {request.service_name}")
        
        # AI 서비스에 문서 생성 요청
        ai_result = request_legal_document_via_tcp(request)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        print(f"[DEBUG] 문서 생성 완료, 소요시간: {generation_time:.2f}초")
        
        # AI 결과 구조화
        response_data = LegalDocumentResponse(
            service_info=ai_result.get("service_info", {}),
            terms_of_service=ai_result.get("terms_of_service", {}),
            privacy_policy=ai_result.get("privacy_policy", {}),
            generation_time=generation_time,
            template_version=ai_result.get("template_version", "1.0"),
            legal_disclaimer="본 문서는 AI에 의해 생성된 가이드라인입니다. 실제 사용 전 반드시 법무 전문가의 검토를 받으시기 바랍니다.",
            review_recommendations=ai_result.get("review_recommendations", [
                "법무팀 또는 변호사 검토 필수",
                "개인정보보호법 준수 여부 확인",
                "서비스 특성에 맞는 조항 추가 검토"
            ])
        )
        
        return SuccessResponse(
            message="법적 문서가 성공적으로 생성되었습니다.",
            data=response_data.model_dump()
        )
        
    except Exception as e:
        print(f"[ERROR] 법적 문서 생성 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"법적 문서 생성 중 오류가 발생했습니다: {str(e)}"
        )

@router.post("/generate-markdown", response_model=SuccessResponse)
async def generate_legal_documents_markdown(
    request: LegalDocumentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    마크다운 형태로 법적 문서를 생성합니다. (복사-붙여넣기 용이)
    """
    start_time = time.time()
    
    try:
        print(f"[DEBUG] 마크다운 법적 문서 생성 요청: {request.service_name}")
        
        # 마크다운 요청을 위해 request에 포맷 정보 추가
        request_dict = request.model_dump()
        request_dict["output_format"] = "markdown"
        
        # AI 서비스에 문서 생성 요청
        modified_request = LegalDocumentRequest(**request_dict)
        ai_result = request_legal_document_via_tcp(modified_request)
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        print(f"[DEBUG] 마크다운 문서 생성 완료, 소요시간: {generation_time:.2f}초")
        
        # 마크다운 응답 구성
        response_data = LegalDocumentMarkdown(
            terms_of_service_markdown=ai_result.get("terms_markdown", ""),
            privacy_policy_markdown=ai_result.get("privacy_markdown", ""),
            combined_document=ai_result.get("combined_markdown", ""),
            legal_notices=[
                "⚠️ 본 문서는 AI 생성 가이드라인입니다",
                "📋 실제 사용 전 법무 검토 필수",
                "🔄 서비스 변경 시 문서도 업데이트 필요",
                "📞 법적 문의는 전문가에게 상담"
            ]
        )
        
        return SuccessResponse(
            message=f"마크다운 법적 문서가 생성되었습니다. (소요시간: {generation_time:.1f}초)",
            data=response_data.model_dump()
        )
        
    except Exception as e:
        print(f"[ERROR] 마크다운 문서 생성 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"마크다운 문서 생성 중 오류: {str(e)}"
        )

@router.post("/project/{project_id}/generate", response_model=SuccessResponse)
async def generate_legal_documents_for_project(
    project_id: int,
    additional_info: dict = {},  # 추가 정보가 있으면 받음
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    기존 프로젝트 정보를 기반으로 법적 문서를 생성합니다.
    """
    # 프로젝트 권한 확인
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    if project.owner_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="프로젝트 소유자만 접근할 수 있습니다.")
    
    try:
        # 프로젝트 정보로 요청 데이터 구성
        request_data = LegalDocumentRequest(
            service_name=project.name,
            service_description=project.description,
            service_type=project.service_type,
            target_audience=additional_info.get("target_audience", "일반 사용자"),
            data_collection=additional_info.get("data_collection", ["이메일", "이름"]),
            data_usage=additional_info.get("data_usage", ["서비스 제공", "고객 지원"]),
            service_features=additional_info.get("service_features", ["회원가입", "기본 기능"]),
            payment_required=additional_info.get("payment_required", False),
            third_party_services=additional_info.get("third_party_services", []),
            age_restriction=additional_info.get("age_restriction"),
            contact_email=additional_info.get("contact_email", "contact@example.com"),
            company_name=additional_info.get("company_name")
        )
        
        # AI 서비스에 요청
        start_time = time.time()
        ai_result = request_legal_document_via_tcp(request_data)
        generation_time = time.time() - start_time
        
        # 응답 구성
        response_data = {
            "project_info": {
                "project_id": project.project_id,
                "project_name": project.name,
                "service_type": project.service_type
            },
            "documents": {
                "service_info": ai_result.get("service_info", {}),
                "terms_of_service": ai_result.get("terms_of_service", {}),
                "privacy_policy": ai_result.get("privacy_policy", {})
            },
            "metadata": {
                "generation_time": generation_time,
                "template_version": ai_result.get("template_version", "1.0"),
                "legal_disclaimer": "프로젝트 기반 생성된 가이드 문서입니다. 법무 검토를 권장합니다."
            }
        }
        
        return SuccessResponse(
            message=f"'{project.name}' 프로젝트의 법적 문서가 생성되었습니다.",
            data=response_data
        )
        
    except Exception as e:
        print(f"[ERROR] 프로젝트 기반 문서 생성 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"문서 생성 오류: {str(e)}"
        )

@router.get("/templates", response_model=SuccessResponse)
async def get_available_templates():
    """
    사용 가능한 법적 문서 템플릿 목록을 조회합니다.
    """
    templates = [
        TemplateInfo(
            template_id="startup_basic",
            name="스타트업 기본 템플릿",
            description="일반적인 스타트업 서비스를 위한 기본 템플릿",
            suitable_for=["APP", "WEB", "AI_SERVICE"],
            compliance_level="STANDARD"
        ),
        TemplateInfo(
            template_id="mobile_app",
            name="모바일 앱 전용",
            description="모바일 앱에 특화된 템플릿 (앱스토어 정책 고려)",
            suitable_for=["APP"],
            compliance_level="COMPREHENSIVE"
        ),
        TemplateInfo(
            template_id="web_service",
            name="웹 서비스 전용",
            description="웹 기반 서비스에 특화된 템플릿",
            suitable_for=["WEB"],
            compliance_level="STANDARD"
        ),
        TemplateInfo(
            template_id="ai_service",
            name="AI 서비스 전용",
            description="AI/ML 서비스를 위한 특화 템플릿",
            suitable_for=["AI_SERVICE"],
            compliance_level="COMPREHENSIVE"
        )
    ]
    
    return SuccessResponse(
        message="사용 가능한 템플릿 목록입니다.",
        data={
            "templates": [template.model_dump() for template in templates],
            "disclaimer": "모든 생성된 문서는 가이드라인이며, 실제 사용 전 법무 검토가 필요합니다.",
            "compliance_standards": [
                "개인정보보호법",
                "정보통신망 이용촉진 및 정보보호 등에 관한 법률",
                "전자상거래 등에서의 소비자보호에 관한 법률"
            ]
        }
    )

@router.get("/sample", response_model=SuccessResponse)
async def get_sample_legal_document():
    """
    샘플 법적 문서를 조회합니다. (AI 서버 테스트 없이)
    """
    sample_data = {
        "service_info": {
            "service_name": "세종 스터디 매칭",
            "service_type": "WEB",
            "description": "대학생들을 위한 스터디 그룹 매칭 서비스"
        },
        "terms_of_service": {
            "title": "세종 스터디 매칭 서비스 이용약관",
            "sections": {
                "purpose": "본 약관은 세종 스터디 매칭 서비스 이용에 관한 기본적인 사항을 규정합니다.",
                "service_description": "학생들 간의 스터디 그룹 형성을 돕는 매칭 플랫폼을 제공합니다.",
                "user_obligations": ["정확한 정보 입력", "타인에 대한 존중", "스터디 약속 준수"]
            }
        },
        "privacy_policy": {
            "title": "개인정보처리방침",
            "sections": {
                "collected_info": ["이메일", "이름", "학과", "학년"],
                "usage_purpose": ["스터디 매칭", "서비스 개선", "고객 지원"],
                "retention_period": "회원 탈퇴 시까지"
            }
        },
        "legal_notices": [
            "본 샘플은 참고용입니다",
            "실제 서비스에는 전문가 검토가 필요합니다"
        ]
    }
    
    return SuccessResponse(
        message="샘플 법적 문서입니다.",
        data=sample_data
    )

@router.get("/test-connection")
async def test_ai_service_connection():
    """
    AI 법적 문서 서비스 연결 상태를 테스트합니다.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            result = s.connect_ex((AI_LEGAL_SERVICE_HOST, AI_LEGAL_SERVICE_PORT))
            
            if result == 0:
                return {"status": "success", "message": f"AI 법적 문서 서비스({AI_LEGAL_SERVICE_HOST}:{AI_LEGAL_SERVICE_PORT}) 연결 성공"}
            else:
                return {"status": "failed", "message": f"AI 법적 문서 서비스 연결 실패 (포트 {AI_LEGAL_SERVICE_PORT})"}
                
    except Exception as e:
        return {"status": "error", "message": f"연결 테스트 중 오류: {str(e)}"}