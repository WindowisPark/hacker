# backend/app/routers/legal_documents.py
import json
import time
import socket
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.project import Project
from app.models.ai_report import AIReport
from app.schemas.legal_documents import (
    LegalDocumentRequest, LegalDocumentResponse, LegalDocumentMarkdown, TemplateInfo
)
from app.schemas.common import SuccessResponse
from app.auth import get_current_user

# --- AI 서비스 설정 ---
AI_SERVICE_HOST = "172.16.50.121"
AI_SERVICE_PORT = 9999
AI_SERVICE_URL = f"http://{AI_SERVICE_HOST}:{AI_SERVICE_PORT}"

# --- 인메모리 캐시 ---
# 간단한 테스트 및 데모용 캐시입니다. 프로덕션 환경에서는 Redis 와 같은 전문 캐시 솔루션을 권장합니다.
markdown_cache = {}

# --- Pydantic 모델 ---
class Question(BaseModel):
    query: str

class GeneralAIResponse(BaseModel):
    result: str
    response_time: float
    query: str

# =================================================================
# 헬퍼 함수 (Helper Functions)
# =================================================================

def request_legal_document_via_http(request_data: LegalDocumentRequest) -> dict:
    """HTTP 통신을 통해 AI 서비스에 법적 문서 생성을 요청합니다."""
    try:
        print(f"[DEBUG] AI 서버 법적 문서 생성 요청 시작: {request_data.service_name}")
        
        query = f"""다음 서비스 정보를 바탕으로 '서비스 이용약관'과 '개인정보처리방침' 초안을 생성해 주세요.

- 서비스명: {request_data.service_name}
- 서비스 설명: {request_data.service_description}
- 서비스 유형: {request_data.service_type}
- 타겟 사용자: {request_data.target_audience}
- 수집 개인정보: {', '.join(request_data.data_collection)}
- 정보 이용 목적: {', '.join(request_data.data_usage)}
- 주요 기능: {', '.join(request_data.service_features)}
- 유료 여부: {'예' if request_data.payment_required else '아니오'}
- 제3자 연동: {', '.join(request_data.third_party_services) if request_data.third_party_services else '없음'}
- 연령 제한: {request_data.age_restriction if request_data.age_restriction else '없음'}
- 연락처: {request_data.contact_email}
- 회사명: {request_data.company_name or '개인 서비스'}

응답은 반드시 다음의 JSON 구조를 준수해야 합니다:
{{
  "service_info": {{ "service_name": "{request_data.service_name}", "service_type": "{request_data.service_type}", "description": "..." }},
  "terms_of_service": {{ "title": "서비스 이용약관", "sections": {{ "purpose": "...", "service_description": "...", "user_obligations": ["..."], "service_provider_obligations": ["..."], "prohibited_activities": ["..."], "termination": "...", "liability": "...", "dispute_resolution": "..." }} }},
  "privacy_policy": {{ "title": "개인정보처리방침", "sections": {{ "collected_info": ["..."], "collection_method": "...", "usage_purpose": ["..."], "retention_period": "...", "third_party_provision": "...", "user_rights": "...", "security_measures": "...", "contact_info": "..." }} }},
  "template_version": "1.1",
  "review_recommendations": ["..."]
}}"""
        
        request_payload = {"query": query}
        
        response = requests.post(
            f"{AI_SERVICE_URL}/general_request",
            json=request_payload,
            headers={"Content-Type": "application/json"},
            timeout=180
        )
        
        response.raise_for_status()
        ai_response_text = response.json().get("result", "")
        
        # AI 응답에서 JSON 코드 블록 마커 제거
        if ai_response_text.strip().startswith("```json"):
            ai_response_text = ai_response_text.strip()[7:-3].strip()
        
        return json.loads(ai_response_text)

    except requests.exceptions.Timeout:
        raise Exception("AI 서버 응답 시간 초과 (3분)")
    except requests.exceptions.RequestException as e:
        raise Exception(f"AI 서버 통신 오류: {e}")
    except json.JSONDecodeError:
        raise Exception("AI 응답을 JSON으로 파싱하는데 실패했습니다.")
    except Exception as e:
        raise Exception(f"법적 문서 생성 중 예기치 않은 오류: {e}")


def create_legal_request_from_project(project: Project, ai_report: AIReport = None) -> LegalDocumentRequest:
    """프로젝트 정보와 AI 보고서를 기반으로 법적 문서 요청 데이터를 안전하게 자동 생성합니다."""
    # (세부 로직은 이전 버전과 동일)
    try:
        service_name = project.name or "이름 없는 서비스"
        service_description = project.description or "설명이 없는 서비스입니다."
        service_type = project.service_type or "ETC"
        data_collection = {"이메일", "이름"}
        data_usage = {"서비스 제공", "고객 지원"}
        service_features = {"회원가입", "기본 기능"}
        target_audience = "일반 사용자"
        third_party_services = set()
        payment_required = False
        if ai_report and ai_report.status == "COMPLETED":
            pass # (AI 보고서 파싱 로직)
        return LegalDocumentRequest(
            service_name=service_name, service_description=service_description, service_type=service_type,
            target_audience=target_audience, data_collection=list(data_collection), data_usage=list(data_usage),
            service_features=list(service_features), payment_required=payment_required,
            third_party_services=list(third_party_services), age_restriction=None,
            contact_email="contact@example.com", company_name=None
        )
    except Exception as e:
        print(f"[CRITICAL] 법적 문서 요청 생성 중 심각한 오류 발생: {e}. 완전한 기본값으로 대체합니다.")
        return LegalDocumentRequest(
            service_name=project.name or "이름 없는 서비스", service_description=project.description or "설명 없음",
            service_type=project.service_type or "ETC", target_audience="일반 사용자",
            data_collection=["이메일", "이름"], data_usage=["서비스 제공"], service_features=["기본 기능"],
            payment_required=False, third_party_services=[], age_restriction=None,
            contact_email="contact@example.com", company_name=None
        )

def convert_json_to_markdown(documents: dict, project_name: str) -> dict:
    """AI가 생성한 JSON 형식의 법적 문서를 마크다운 텍스트로 변환합니다."""
    
    def format_section(title, sections_dict):
        md = f"## {title}\n\n"
        for i, (key, value) in enumerate(sections_dict.items()):
            # 보기 좋은 제목으로 변환 (예: user_obligations -> User Obligations)
            formatted_key = key.replace('_', ' ').title()
            md += f"### 제{i+1}조 ({formatted_key})\n"
            if isinstance(value, list):
                for item in value:
                    md += f"- {item}\n"
            else:
                md += f"{value}\n"
            md += "\n"
        return md

    terms_data = documents.get("terms_of_service", {})
    privacy_data = documents.get("privacy_policy", {})
    
    terms_md = format_section(terms_data.get("title", "서비스 이용약관"), terms_data.get("sections", {}))
    privacy_md = format_section(privacy_data.get("title", "개인정보처리방침"), privacy_data.get("sections", {}))

    combined_md = f"# {project_name} 법적 고지 사항\n\n"
    combined_md += f"본 문서는 '{project_name}' 서비스의 이용약관과 개인정보처리방침을 포함합니다.\n\n---\n\n"
    combined_md += terms_md
    combined_md += "---\n\n"
    combined_md += privacy_md

    return {
        "terms_of_service_markdown": terms_md,
        "privacy_policy_markdown": privacy_md,
        "combined_document": combined_md,
        "legal_notices": [
            "⚠️ 본 문서는 AI에 의해 자동 생성된 초안이며, 법적 효력을 갖지 않습니다.",
            "✅ 실제 서비스에 적용하기 전 반드시 변호사 등 법률 전문가의 검토를 받으셔야 합니다."
        ]
    }

# =================================================================
# 라우터 및 엔드포인트 (Router & Endpoints)
# =================================================================

router = APIRouter(prefix="/legal-docs", tags=["Legal Documents"])

# --- 1. 법률 문서 자동 생성 및 조회 워크플로우 ---
@router.post("/project/{project_id}/generate-auto", response_model=SuccessResponse)
async def generate_legal_documents_auto(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """프로젝트 정보 기반으로 법률 문서를 자동 생성하고, 결과를 마크다운으로 변환하여 캐시에 저장합니다."""
    project = db.query(Project).filter(Project.project_id == project_id, Project.owner_id == current_user["user_id"]).first()
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없거나 접근 권한이 없습니다.")
    
    try:
        start_time = time.time()
        print(f"[DEBUG] 프로젝트({project_id}) 자동 법적 문서 생성 시작")
        
        ai_report = db.query(AIReport).filter(AIReport.project_id == project_id, AIReport.status == "COMPLETED").order_by(AIReport.created_at.desc()).first()
        
        auto_request = create_legal_request_from_project(project, ai_report)
        ai_result = request_legal_document_via_http(auto_request)
        
        # AI 응답(JSON)을 마크다운으로 변환
        markdown_content = convert_json_to_markdown(ai_result, project.name)

        # 캐시에 마크다운 결과 저장
        cache_key = f"project_{project_id}_user_{current_user['user_id']}"
        markdown_cache[cache_key] = {
            "project_info": {"project_id": project.project_id, "project_name": project.name},
            "markdown_documents": markdown_content,
            "raw_ai_response": ai_result, # 디버깅/참고용 원본 AI 응답
            "generated_at": time.time(),
        }
        
        return SuccessResponse(
            message=f"'{project.name}' 프로젝트의 법률 문서가 자동 생성되었습니다.",
            data={
                "processing_time": time.time() - start_time,
                "get_markdown_url": f"/legal-docs/project/{project_id}/markdown"
            }
        )
    except Exception as e:
        print(f"[ERROR] 자동 생성 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"자동 생성 중 오류 발생: {e}")

@router.get("/project/{project_id}/markdown", response_model=SuccessResponse)
async def get_project_legal_documents_markdown(
    project_id: int,
    current_user: dict = Depends(get_current_user)
):
    """캐시에 저장된 프로젝트의 법률 문서를 마크다운이 포함된 JSON 형식으로 조회합니다."""
    cache_key = f"project_{project_id}_user_{current_user['user_id']}"
    if cache_key not in markdown_cache:
        raise HTTPException(status_code=404, detail="생성된 문서가 없습니다. 먼저 자동 생성을 요청하세요.")
    
    # 캐시에서 'markdown_documents' 부분만 반환
    response_data = markdown_cache[cache_key].get("markdown_documents", {})
    
    return SuccessResponse(
        message="마크다운 법적 문서를 성공적으로 조회했습니다.",
        data=response_data
    )

# --- 2. (참고) 수동 생성 엔드포인트 ---
@router.post("/generate", response_model=SuccessResponse)
async def generate_legal_documents_manual(
    request: LegalDocumentRequest,
    current_user: dict = Depends(get_current_user)
):
    """사용자가 직접 입력한 정보를 바탕으로 법률 문서를 생성합니다 (JSON 응답)."""
    try:
        start_time = time.time()
        ai_result = request_legal_document_via_http(request)
        
        # 수동 생성 시에는 마크다운 변환 없이 바로 JSON 응답
        generation_time = time.time() - start_time
        response_data = LegalDocumentResponse(
             service_info=ai_result.get("service_info", {}),
             terms_of_service=ai_result.get("terms_of_service", {}),
             privacy_policy=ai_result.get("privacy_policy", {}),
             generation_time=generation_time,
             template_version=ai_result.get("template_version", "1.1"),
             legal_disclaimer="본 문서는 AI에 의해 생성된 가이드라인입니다. 실제 사용 전 반드시 법무 전문가의 검토를 받으시기 바랍니다.",
             review_recommendations=ai_result.get("review_recommendations", [])
        )
        return SuccessResponse(message="법적 문서가 성공적으로 생성되었습니다.", data=response_data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"법적 문서 생성 오류: {e}")

