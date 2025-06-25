# backend/app/schemas/legal_documents.py
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# 법적 문서 생성 요청 (간단 버전)
class LegalDocumentRequest(BaseModel):
    service_name: str  # 서비스명
    service_description: str  # 서비스 설명
    service_type: str  # APP, WEB, AI_SERVICE, ETC
    target_audience: str  # 타겟 사용자층 (일반 사용자, 기업, 학생 등)
    data_collection: List[str]  # 수집하는 개인정보 유형 ['이메일', '이름', '전화번호', '사용로그' 등]
    data_usage: List[str]  # 개인정보 이용 목적 ['서비스 제공', '고객 지원', '마케팅' 등]
    service_features: List[str]  # 주요 서비스 기능 ['회원가입', '결제', '커뮤니티' 등]
    payment_required: bool = False  # 유료 서비스 여부
    third_party_services: List[str] = []  # 제3자 서비스 연동 ['결제 서비스', 'SNS 로그인', '지도 API' 등]
    age_restriction: Optional[int] = None  # 최소 연령 제한
    contact_email: str = "contact@example.com"  # 연락처 이메일
    company_name: Optional[str] = None  # 회사명 (있는 경우)

# 생성된 문서 응답
class LegalDocumentResponse(BaseModel):
    service_info: Dict[str, Any]  # 서비스 기본 정보
    terms_of_service: Dict[str, Any]  # 서비스 이용약관
    privacy_policy: Dict[str, Any]  # 개인정보처리방침
    
    # 생성 메타데이터
    generation_time: float  # 생성 소요 시간 (초)
    template_version: str  # 사용된 템플릿 버전
    legal_disclaimer: str  # 법적 고지사항
    review_recommendations: List[str]  # 검토 권장사항

# 간단한 응답 포맷 (마크다운 형태)
class LegalDocumentMarkdown(BaseModel):
    terms_of_service_markdown: str  # 이용약관 마크다운
    privacy_policy_markdown: str  # 개인정보처리방침 마크다운
    combined_document: str  # 통합 문서 마크다운
    legal_notices: List[str]  # 주요 법적 주의사항

# 템플릿 정보
class TemplateInfo(BaseModel):
    template_id: str
    name: str
    description: str
    suitable_for: List[str]  # 적합한 서비스 유형
    compliance_level: str  # 컴플라이언스 수준 (BASIC, STANDARD, COMPREHENSIVE)