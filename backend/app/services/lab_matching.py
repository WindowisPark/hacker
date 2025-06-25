# backend/app/services/lab_matching.py
import json
import re
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.research_lab import ResearchLab, Professor, Department, ProjectLabMatching
from app.models.project import Project
from app.schemas.research_lab import ProjectMatchingRequest, ProjectLabMatchingCreate

class LabMatchingService:
    """연구실-프로젝트 매칭 서비스"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # 기술 스택 매핑 (프로젝트에서 사용하는 용어 -> 연구실 기술스택)
        self.tech_mapping = {
            'ai': ['AI', 'Machine Learning', 'Deep Learning', '인공지능', '머신러닝', '딥러닝'],
            'ml': ['Machine Learning', 'AI', 'Deep Learning', '머신러닝', '인공지능'],
            'web': ['Web', 'Frontend', 'Backend', '웹개발', 'JavaScript', 'React', 'Node.js'],
            'app': ['Mobile', 'Android', 'iOS', 'React Native', 'Flutter', '모바일'],
            'data': ['Data Science', 'Big Data', 'Analytics', '데이터사이언스', '빅데이터'],
            'iot': ['IoT', 'Internet of Things', 'Sensor', '사물인터넷', '센서'],
            'blockchain': ['Blockchain', 'Cryptocurrency', '블록체인'],
            'ar': ['AR', 'Augmented Reality', '증강현실'],
            'vr': ['VR', 'Virtual Reality', '가상현실'],
            'cv': ['Computer Vision', 'Image Processing', '컴퓨터비전', '영상처리'],
            'nlp': ['NLP', 'Natural Language Processing', '자연어처리'],
            'robotics': ['Robotics', 'Robot', '로봇', '로보틱스'],
            'security': ['Security', 'Cybersecurity', '보안', '사이버보안']
        }
        
        # 산업별 연구 분야 매핑
        self.industry_mapping = {
            'healthcare': ['의료', '헬스케어', 'Medical', 'Biomedical', '바이오메디컬'],
            'automotive': ['자동차', '자율주행', 'Automotive', 'Autonomous Vehicle'],
            'fintech': ['금융', 'FinTech', '블록체인', 'Blockchain'],
            'education': ['교육', 'Education', 'EdTech', '학습'],
            'entertainment': ['엔터테인먼트', 'Entertainment', '게임', 'Game'],
            'environment': ['환경', 'Environment', '기후', 'Climate'],
            'manufacturing': ['제조', 'Manufacturing', '산업', 'Industrial']
        }

    def calculate_similarity_score(self, project: Project, lab: ResearchLab) -> Tuple[float, Dict]:
        """프로젝트와 연구실 간의 유사도 점수 계산"""
        scores = {}
        factors = {}
        
        # 1. 서비스 타입 매칭 (30%)
        service_score = self._calculate_service_type_score(project, lab)
        scores['service_type'] = service_score
        factors['service_type'] = f"서비스 타입: {project.service_type}"
        
        # 2. 기술 스택 매칭 (25%)
        tech_score = self._calculate_tech_stack_score(project, lab)
        scores['tech_stack'] = tech_score
        factors['tech_stack'] = "기술 스택 관련성"
        
        # 3. 연구 분야 키워드 매칭 (25%)
        keyword_score = self._calculate_keyword_score(project, lab)
        scores['keywords'] = keyword_score
        factors['keywords'] = "연구 분야 키워드 매칭"
        
        # 4. 프로젝트 설명과 연구실 설명 유사도 (20%)
        description_score = self._calculate_description_score(project, lab)
        scores['description'] = description_score
        factors['description'] = "프로젝트-연구실 설명 유사도"
        
        # 가중 평균 계산
        total_score = (
            scores['service_type'] * 0.3 +
            scores['tech_stack'] * 0.25 +
            scores['keywords'] * 0.25 +
            scores['description'] * 0.2
        )
        
        return total_score, {
            'scores': scores,
            'factors': factors,
            'total_score': total_score
        }

    def _calculate_service_type_score(self, project: Project, lab: ResearchLab) -> float:
        """서비스 타입 기반 점수 계산"""
        service_keywords = {
            'APP': ['모바일', 'Mobile', 'Android', 'iOS', 'App'],
            'WEB': ['웹', 'Web', 'Frontend', 'Backend', '웹개발'],
            'AI': ['AI', '인공지능', 'Machine Learning', '머신러닝', '딥러닝']
        }
        
        project_keywords = service_keywords.get(project.service_type, [])
        lab_keywords = lab.keywords.lower() if lab.keywords else ""
        lab_research = lab.research_areas.lower() if lab.research_areas else ""
        
        matches = 0
        for keyword in project_keywords:
            if keyword.lower() in lab_keywords or keyword.lower() in lab_research:
                matches += 1
        
        return min(matches / len(project_keywords) if project_keywords else 0, 1.0)

    def _calculate_tech_stack_score(self, project: Project, lab: ResearchLab) -> float:
        """기술 스택 기반 점수 계산"""
        if not lab.tech_stack:
            return 0.0
        
        try:
            lab_tech = json.loads(lab.tech_stack)
            lab_tech_str = " ".join(lab_tech).lower()
        except:
            lab_tech_str = lab.tech_stack.lower()
        
        # 프로젝트 타입에 따른 기술 매칭
        project_techs = []
        if project.service_type == 'APP':
            project_techs = ['mobile', 'android', 'ios', 'react native', 'flutter']
        elif project.service_type == 'WEB':
            project_techs = ['web', 'javascript', 'react', 'vue', 'python', 'node.js']
        elif project.service_type == 'AI':
            project_techs = ['python', 'tensorflow', 'pytorch', 'ai', 'ml']
        
        matches = sum(1 for tech in project_techs if tech in lab_tech_str)
        return min(matches / len(project_techs) if project_techs else 0, 1.0)

    def _calculate_keyword_score(self, project: Project, lab: ResearchLab) -> float:
        """키워드 기반 점수 계산"""
        project_desc = (project.description + " " + (project.idea_name or "")).lower()
        lab_keywords = (lab.keywords or "").lower()
        
        # 공통 키워드 추출
        common_words = [
            'ai', '인공지능', 'ml', '머신러닝', 'data', '데이터', 'web', '웹',
            'mobile', '모바일', 'app', '앱', 'iot', '사물인터넷', 'security', '보안',
            'robot', '로봇', 'vision', '비전', 'nlp', '자연어'
        ]
        
        matches = 0
        total_keywords = 0
        
        for word in common_words:
            if word in project_desc:
                total_keywords += 1
                if word in lab_keywords:
                    matches += 1
        
        return matches / total_keywords if total_keywords > 0 else 0.0

    def _calculate_description_score(self, project: Project, lab: ResearchLab) -> float:
        """설명 유사도 기반 점수 계산"""
        project_text = (project.description + " " + (project.idea_name or "")).lower()
        lab_text = ((lab.description or "") + " " + (lab.keywords or "")).lower()
        
        # 간단한 단어 기반 유사도 계산
        project_words = set(re.findall(r'\w+', project_text))
        lab_words = set(re.findall(r'\w+', lab_text))
        
        if not project_words or not lab_words:
            return 0.0
        
        intersection = project_words.intersection(lab_words)
        union = project_words.union(lab_words)
        
        return len(intersection) / len(union) if union else 0.0

    def find_matching_labs(self, request: ProjectMatchingRequest) -> List[Dict]:
        """프로젝트에 매칭되는 연구실 찾기"""
        # 프로젝트 조회
        project = self.db.query(Project).filter(Project.project_id == request.project_id).first()
        if not project:
            return []
        
        # 활성 연구실 조회
        labs = self.db.query(ResearchLab).filter(ResearchLab.is_active == True).all()
        
        matches = []
        for lab in labs:
            score, details = self.calculate_similarity_score(project, lab)
            
            if score >= request.min_score:
                # 교수 및 학과 정보 조회
                professor = self.db.query(Professor).filter(Professor.professor_id == lab.director_id).first()
                department = None
                if professor:
                    department = self.db.query(Department).filter(Department.department_id == professor.department_id).first()
                
                match_data = {
                    'lab_id': lab.lab_id,
                    'lab_name': lab.name,
                    'lab_name_en': lab.name_en,
                    'location': lab.location,
                    'director_name': professor.name if professor else None,
                    'department_name': department.name if department else None,
                    'research_areas': lab.research_areas,
                    'description': lab.description,
                    'similarity_score': score,
                    'matching_details': details,
                    'contact_info': {
                        'email': professor.email if professor else lab.email,
                        'phone': professor.phone if professor else lab.phone
                    }
                }
                matches.append(match_data)
        
        # 점수 순으로 정렬
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # 최대 결과 수 제한
        return matches[:request.max_results]

    def save_matching_results(self, project_id: int, matches: List[Dict]) -> None:
        """매칭 결과를 데이터베이스에 저장"""
        # 기존 매칭 결과 삭제
        self.db.query(ProjectLabMatching).filter(
            ProjectLabMatching.project_id == project_id
        ).delete()
        
        # 새로운 매칭 결과 저장
        for match in matches:
            matching_record = ProjectLabMatching(
                project_id=project_id,
                lab_id=match['lab_id'],
                similarity_score=match['similarity_score'],
                matching_reason=f"유사도 점수: {match['similarity_score']:.2f}",
                matching_factors=json.dumps(match['matching_details'], ensure_ascii=False),
                status="SUGGESTED"
            )
            self.db.add(matching_record)
        
        self.db.commit()

    def get_project_matching_history(self, project_id: int) -> List[Dict]:
        """프로젝트의 매칭 이력 조회"""
        matchings = self.db.query(ProjectLabMatching).filter(
            ProjectLabMatching.project_id == project_id
        ).order_by(ProjectLabMatching.similarity_score.desc()).all()
        
        results = []
        for matching in matchings:
            lab = self.db.query(ResearchLab).filter(ResearchLab.lab_id == matching.lab_id).first()
            if lab:
                professor = self.db.query(Professor).filter(Professor.professor_id == lab.director_id).first()
                department = None
                if professor:
                    department = self.db.query(Department).filter(Department.department_id == professor.department_id).first()
                
                result = {
                    'matching_id': matching.matching_id,
                    'lab_id': lab.lab_id,
                    'lab_name': lab.name,
                    'director_name': professor.name if professor else None,
                    'department_name': department.name if department else None,
                    'similarity_score': matching.similarity_score,
                    'status': matching.status,
                    'created_at': matching.created_at,
                    'matching_factors': json.loads(matching.matching_factors) if matching.matching_factors else {}
                }
                results.append(result)
        
        return results