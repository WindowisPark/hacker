# backend/integrated_data_setup.py
"""
세종 스타트업 네비게이터 + 연구실 매칭 시스템
통합 데이터 삽입 스크립트
"""

import sqlite3
import json
from datetime import datetime, timedelta

def create_tables_if_not_exists(cursor):
    """필요한 테이블들이 없으면 생성"""
    
    # 학과 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            name_en VARCHAR(200),
            college VARCHAR(200) DEFAULT '인공지능융합대학',
            description TEXT,
            building VARCHAR(100),
            phone VARCHAR(50),
            email VARCHAR(200),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 교수 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS professors (
            professor_id INTEGER PRIMARY KEY,
            department_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            name_en VARCHAR(100),
            position VARCHAR(50),
            email VARCHAR(200),
            phone VARCHAR(50),
            office_location VARCHAR(200),
            research_fields TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments (department_id)
        )
    """)
    
    # 연구실 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS research_labs (
            lab_id INTEGER PRIMARY KEY,
            director_id INTEGER NOT NULL,
            name VARCHAR(200) NOT NULL,
            name_en VARCHAR(200),
            location VARCHAR(200),
            phone VARCHAR(50),
            email VARCHAR(200),
            website VARCHAR(500),
            research_areas TEXT,
            keywords TEXT,
            description TEXT,
            tech_stack TEXT,
            collaboration_history TEXT,
            recent_projects TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (director_id) REFERENCES professors (professor_id)
        )
    """)
    
    # 프로젝트-연구실 매칭 테이블
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_lab_matchings (
            matching_id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            lab_id INTEGER NOT NULL,
            similarity_score REAL,
            matching_reason TEXT,
            matching_factors TEXT,
            status VARCHAR(50) DEFAULT 'SUGGESTED',
            contacted_at DATETIME,
            response_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (project_id),
            FOREIGN KEY (lab_id) REFERENCES research_labs (lab_id)
        )
    """)

def insert_all_data():
    """전체 데이터 삽입"""
    conn = sqlite3.connect('sejong_startup.db')
    cursor = conn.cursor()
    
    try:
        print("🚀 세종 스타트업 네비게이터 + 연구실 매칭 시스템 데이터 설정을 시작합니다...")
        
        # 테이블 생성
        create_tables_if_not_exists(cursor)
        print("✅ 테이블 생성 완료")
        
        # 1. 학과 데이터 삽입
        print("\n🏛️ 학과 데이터 추가 중...")
        departments_data = [
            ('컴퓨터공학과', 'Computer Science and Engineering', '대양AI센터', '컴퓨터 하드웨어부터 인공지능까지 컴퓨터 과학 전반을 다루는 핵심 학과'),
            ('정보보호학과', 'Information Security', '대양AI센터', '사이버 보안과 정보보호 기술을 전문으로 하는 학과'),
            ('콘텐츠소프트웨어학과', 'Content Software', '대양AI센터', '소프트웨어와 디지털 콘텐츠 기술을 융합하는 창의적 학과'),
            ('인공지능데이터사이언스학과', 'AI and Data Science', '대양AI센터', 'AI와 데이터 과학의 핵심 방법론을 연구하는 최첨단 학과'),
            ('AI로봇학과', 'AI Robotics', '대양AI센터', '지능형 로봇과 무인 시스템을 개발하는 학과'),
            ('AI융합전자공학과', 'AI and Electronic Convergence Engineering', '대양AI센터', '전자공학과 AI 기술을 융합하는 학과'),
            ('지능정보융합학과', 'Intelligent Information Convergence', '대양AI센터', 'AI와 IoT를 결합한 물리-가상 융합 시스템 전문 학과'),
        ]
        
        for dept_data in departments_data:
            cursor.execute("""
                INSERT OR IGNORE INTO departments (name, name_en, college, building, description, created_at)
                VALUES (?, ?, '인공지능융합대학', ?, ?, datetime('now'))
            """, dept_data)
        
        print(f"✅ {len(departments_data)}개 학과 추가 완료")
        
        # 2. 교수 데이터 삽입
        print("\n👨‍🏫 교수 데이터 추가 중...")
        professors_data = [
            # 컴퓨터공학과 (department_id: 1)
            (1, '박태순', 'Taesoon Park', '교수', None, '02-3408-3240', '대양AI센터 823호', '분산처리시스템,클라우드컴퓨팅'),
            (1, '신동일', 'Dongil Shin', '교수', None, '02-3408-3241', '대양AI센터 825호', '데이터베이스,DBMS'),
            (1, '이강원', 'Kangwon Lee', '교수', None, '02-3408-3489', '집현관 910호', '네트워크,클라우드,AI,데이터,스마트팩토리'),
            (1, '문현준', 'Hyunjun Moon', '교수', None, '02-3408-3874', '대양AI센터 819호', '인공지능,패턴인식,머신러닝'),
            (1, '한동일', 'Dongil Han', '교수', None, '02-3408-3751', '대양AI센터 721호', '컴퓨터비전,영상처리'),
            (1, '최수미', 'Sumi Choi', '교수', None, '02-3408-3754', '대양AI센터 720호', '컴퓨터그래픽스,3D'),
            
            # 정보보호학과 (department_id: 2)
            (2, '이종혁', 'Jonghyouk Lee', '부교수', 'jonghyouk@sejong.ac.kr', '02-3408-1846', '대양AI센터 803호', '사이버보안,프로토콜분석,오펜시브보안'),
            (2, '신지선', 'Jiseon Shin', '부교수', 'jsshin@sejong.ac.kr', '02-3408-3888', '대양AI센터 708호', '암호학,인증,AI보안,블록체인보안,드론보안'),
            (2, '김영갑', 'Younggab Kim', '교수', 'alwaysgabi@sejong.ac.kr', '02-6935-2424', '대양AI센터 701호', '시스템보안,보안공학,AI영상보안,IoT보안'),
            
            # 콘텐츠소프트웨어학과 (department_id: 3)
            (3, '백성욱', 'Seongwook Baik', '교수', 'sbaik@sejong.ac.kr', '02-3408-3797', '대양AI센터 622호', '컴퓨터비전,데이터마이닝,비주얼마이닝,문화재복원'),
            (3, '이종원', 'Jongwon Lee', '교수', 'jwlee@sejong.ac.kr', '02-3408-3798', '대양AI센터 619호', '증강현실,가상현실,3D상호작용,HCI'),
            (3, '변재욱', 'Jaeuk Byun', '조교수', 'jwbyun@sejong.ac.kr', '02-3408-1847', '대양AI센터 604호', '데이터마이닝,IoT,시간그래프,그래프신경망'),
            (3, '이은상', 'Eunsang Lee', '조교수', 'eslee3209@sejong.ac.kr', '02-3408-2975', '대양AI센터 621호', '프라이버시보호ML,연합학습,차분프라이버시'),
            
            # 인공지능데이터사이언스학과 (department_id: 4)
            (4, '유성준', 'Sungjun Yoo', '석좌교수', 'sjyoo@sejong.ac.kr', '02-3408-3755', '대양AI센터 719호', '인공지능,머신러닝,빅데이터'),
            (4, '구영현', 'Younghyun Koo', '조교수', None, '02-3408-3253', '대양AI센터 801호', '인공지능,메타러닝,의료영상분석'),
            (4, '박동현', 'Donghyun Park', '조교수', None, '02-3408-1946', '대양AI센터 707호', '데이터마이닝,음식AI,자연어처리,추천시스템'),
            (4, '심태용', 'Taeyong Shim', '조교수', None, '02-3408-1886', '대양AI센터 518호', '생성AI,바이오메디컬,단백질구조예측'),
            (4, '최우석', 'Wooseok Choi', '조교수', 'wschoi@sejong.ac.kr', None, None, '기후환경,데이터사이언스,디지털트윈,자연재해예측'),
            
            # AI로봇학과 (department_id: 5)
            (5, '임유승', 'Yuseung Lim', '교수', None, None, None, '지능형반도체,뉴로모픽소자,전력반도체,바이오센서'),
            (5, '송진우', 'Jinwoo Song', '교수', 'jwsong@sejong.ac.kr', None, None, '지능항법,제어시스템,무인시스템,센서융합'),
            (5, '서재규', 'Jaekyu Suhr', '교수', 'jksuhr@sejong.ac.kr', None, None, '자율주행,차량인식,컴퓨터비전,LIDAR,센서융합'),
            (5, '강병현', 'Byunghyun Kang', '교수', 'brianbkang@sejong.ac.kr', None, None, '지능로봇,로봇학습,인간로봇상호작용,협업로봇'),
        ]
        
        for prof_data in professors_data:
            cursor.execute("""
                INSERT OR IGNORE INTO professors (department_id, name, name_en, position, email, phone, office_location, research_fields, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, prof_data)
        
        print(f"✅ {len(professors_data)}명의 교수 추가 완료")
        
        # 3. 연구실 데이터 삽입
        print("\n🔬 연구실 데이터 추가 중...")
        research_labs_data = [
            # 컴퓨터공학과 연구실
            (1, '분산처리시스템 연구실', 'Distributed Processing Systems Lab', '대양AI센터 823호', None, None, None,
             json.dumps(['분산시스템', '클라우드컴퓨팅', '병렬처리'], ensure_ascii=False),
             '분산처리,클라우드,병렬처리,고성능컴퓨팅,마이크로서비스',
             '대규모 분산 시스템의 성능 최적화와 신뢰성 향상을 연구합니다.',
             json.dumps(['Java', 'Python', 'Kubernetes', 'Docker', 'Apache Spark'], ensure_ascii=False)),
            
            (2, '데이터베이스 연구실', 'Database Lab', '대양AI센터 825호', None, None, None,
             json.dumps(['데이터베이스시스템', 'DBMS', '빅데이터'], ensure_ascii=False),
             '데이터베이스,DBMS,빅데이터,데이터마이닝,SQL,NoSQL',
             '차세대 데이터베이스 시스템과 빅데이터 처리 기술을 연구합니다.',
             json.dumps(['SQL', 'NoSQL', 'Hadoop', 'Spark', 'MongoDB'], ensure_ascii=False)),
            
            (4, '인공지능-빅데이터 연구센터', 'AI & Big Data Research Center', '대양AI센터 819호', None, None, None,
             json.dumps(['인공지능', '머신러닝', '빅데이터', '패턴인식'], ensure_ascii=False),
             'AI,머신러닝,딥러닝,빅데이터,패턴인식,데이터분석',
             '인공지능과 빅데이터 기술을 활용한 지능형 시스템 개발을 연구합니다.',
             json.dumps(['Python', 'TensorFlow', 'PyTorch', 'Spark', 'R'], ensure_ascii=False)),
            
            (5, '컴퓨터비전 연구실', 'Computer Vision Lab', '대양AI센터 721호', None, None, None,
             json.dumps(['컴퓨터비전', '영상처리', '딥러닝'], ensure_ascii=False),
             '컴퓨터비전,영상처리,딥러닝,이미지분석,객체인식',
             '컴퓨터 비전과 영상 처리 기술을 통한 지능형 시각 시스템을 개발합니다.',
             json.dumps(['Python', 'OpenCV', 'TensorFlow', 'PyTorch'], ensure_ascii=False)),
            
            # 정보보호학과 연구실
            (8, '정보보호 연구실', 'Information Security Lab', '대양AI센터 708호', None, 'jsshin@sejong.ac.kr', None,
             json.dumps(['암호학', '인증기술', 'AI보안', '블록체인보안'], ensure_ascii=False),
             '암호학,인증,AI보안,블록체인,드론보안,사이버보안',
             'AI와 블록체인 시대의 새로운 보안 위협에 대응하는 기술을 연구합니다.',
             json.dumps(['Python', 'C++', 'Blockchain', 'AI/ML'], ensure_ascii=False)),
            
            (9, '보안공학 연구실', 'Security Engineering Lab', '대양AI센터 701호', None, 'alwaysgabi@sejong.ac.kr', None,
             json.dumps(['시스템보안', '보안공학', 'AI영상보안', 'IoT보안'], ensure_ascii=False),
             '시스템보안,보안공학,AI영상보안,IoT보안,CCTV보안',
             'AI 기반 영상 보안과 IoT 시스템 보안을 전문으로 연구합니다.',
             json.dumps(['Python', 'C/C++', 'AI/ML', 'IoT'], ensure_ascii=False)),
            
            # 콘텐츠소프트웨어학과 연구실
            (10, '지능형 미디어 연구실', 'Intelligent Media Lab', '대양AI센터 622호', None, 'sbaik@sejong.ac.kr', None,
             json.dumps(['컴퓨터비전', '데이터마이닝', '비주얼마이닝', '문화재복원'], ensure_ascii=False),
             '컴퓨터비전,데이터마이닝,비주얼마이닝,AI비디오,문화재복원',
             '인공지능 기반 비디오 요약과 문화재 복원 기술을 연구합니다.',
             json.dumps(['Python', 'OpenCV', 'TensorFlow', 'Unity'], ensure_ascii=False)),
            
            (11, 'Mixed Reality & Interaction Lab', 'Mixed Reality & Interaction Lab', '대양AI센터 619호', None, 'jwlee@sejong.ac.kr', None,
             json.dumps(['증강현실', '가상현실', '3D상호작용', 'HCI'], ensure_ascii=False),
             'AR,VR,MR,증강현실,가상현실,3D,HCI,상호작용',
             '모바일 기반 증강현실과 3차원 공간 상호작용 기술을 연구합니다.',
             json.dumps(['Unity', 'C#', 'ARCore', 'ARKit', 'OpenGL'], ensure_ascii=False)),
            
            (12, 'Data Frameworks and Platforms Lab', 'DFPL', '대양AI센터 604호', None, 'jwbyun@sejong.ac.kr', None,
             json.dumps(['데이터마이닝', 'IoT', 'TemporalGraph', '그래프신경망'], ensure_ascii=False),
             '데이터마이닝,IoT,시간그래프,그래프신경망,GNN,데이터플랫폼',
             '시간에 따라 변화하는 그래프 데이터 처리 프레임워크를 연구합니다.',
             json.dumps(['Python', 'NetworkX', 'PyTorch Geometric', 'Neo4j'], ensure_ascii=False)),
            
            (13, '프라이버시보호 AI 연구실', 'Privacy-Preserving AI Lab', '대양AI센터 621호', None, 'eslee3209@sejong.ac.kr', None,
             json.dumps(['프라이버시보호ML', '연합학습', '차분프라이버시'], ensure_ascii=False),
             '프라이버시,연합학습,차분프라이버시,보안AI,개인정보보호',
             '개인정보를 보호하면서 AI 모델을 학습하는 기술을 연구합니다.',
             json.dumps(['Python', 'TensorFlow', 'PySyft', 'Opacus'], ensure_ascii=False)),
            
            # 인공지능데이터사이언스학과 연구실
            (14, 'AI-빅데이터 연구센터', 'AI & Big Data Research Center', '대양AI센터 719호', None, 'sjyoo@sejong.ac.kr', None,
             json.dumps(['인공지능', '빅데이터', '머신러닝', '산업AI'], ensure_ascii=False),
             'AI,빅데이터,머신러닝,산업AI,데이터분석,정부과제',
             '47억원 규모 정부과제를 수행하는 국내 최고 수준의 AI 연구센터입니다.',
             json.dumps(['Python', 'TensorFlow', 'PyTorch', 'Spark', 'Hadoop'], ensure_ascii=False)),
            
            (16, 'FNAI Lab', 'Food & AI Lab', '대양AI센터 707호', None, None, None,
             json.dumps(['음식정보학', 'NLP', '추천시스템', '레시피생성'], ensure_ascii=False),
             '음식AI,음식정보학,NLP,추천시스템,레시피,요리',
             '자연어 처리를 활용한 개인화 음식 추천과 레시피 생성을 연구합니다.',
             json.dumps(['Python', 'BERT', 'GPT', 'Recommendation Systems'], ensure_ascii=False)),
            
            (17, '생성AI 및 바이오메디컬 연구실', 'Generative AI & Biomedical Lab', '대양AI센터 518호', None, None, None,
             json.dumps(['생성AI', '바이오메디컬', '단백질구조예측'], ensure_ascii=False),
             '생성AI,바이오메디컬,단백질,구조예측,신약개발,의료AI',
             '생성 AI를 활용한 단백질 구조 예측과 신약 개발을 연구합니다.',
             json.dumps(['Python', 'PyTorch', 'AlphaFold', 'RDKit'], ensure_ascii=False)),
            
            (18, '기후환경 데이터사이언스 연구실', 'Climate & Environmental Data Science Lab', None, None, 'wschoi@sejong.ac.kr', None,
             json.dumps(['기후환경', '데이터사이언스', '디지털트윈', '자연재해예측'], ensure_ascii=False),
             '기후,환경,데이터사이언스,디지털트윈,자연재해,기상예측',
             '빅데이터와 AI를 활용한 기후 변화와 자연재해 예측을 연구합니다.',
             json.dumps(['Python', 'R', 'TensorFlow', 'Climate Models'], ensure_ascii=False)),
            
            # AI로봇학과 연구실
            (19, 'Intelligent Semiconductor Laboratory', 'ISLab', None, None, None, None,
             json.dumps(['지능형반도체', '뉴로모픽', '전력반도체', '바이오센서'], ensure_ascii=False),
             '반도체,뉴로모픽,전력반도체,바이오센서,AI칩,저전력',
             '뉴로모픽 소자와 AI 전용 반도체를 개발합니다. 21억원 이상의 대형 연구비를 보유하고 있습니다.',
             json.dumps(['VHDL', 'Verilog', 'SPICE', 'MATLAB'], ensure_ascii=False)),
            
            (20, 'Intelligent Navigation and Control Systems Lab', 'INCSL', None, None, 'jwsong@sejong.ac.kr', None,
             json.dumps(['지능항법', '제어시스템', '무인시스템', '센서융합'], ensure_ascii=False),
             '항법,제어,무인시스템,드론,자율주행,센서융합',
             '무인 시스템을 위한 지능형 항법과 제어 알고리즘을 연구합니다.',
             json.dumps(['MATLAB', 'Simulink', 'ROS', 'C++'], ensure_ascii=False)),
            
            (21, 'Intelligent Vehicle Perception Lab', 'IVPL', None, None, 'jksuhr@sejong.ac.kr', None,
             json.dumps(['자율주행', '차량인식', '컴퓨터비전', 'LIDAR'], ensure_ascii=False),
             '자율주행,차량인식,LIDAR,레이더,센서융합,객체인식',
             '자율주행차량의 환경 인식과 센서 융합 기술을 연구합니다.',
             json.dumps(['Python', 'C++', 'ROS', 'PCL', 'OpenCV'], ensure_ascii=False)),
            
            (22, 'Intelligent Robotics Lab', 'IRL', None, None, 'brianbkang@sejong.ac.kr', None,
             json.dumps(['지능로봇', '로봇학습', '인간로봇상호작용'], ensure_ascii=False),
             '지능로봇,로봇학습,HRI,인간로봇상호작용,협업로봇',
             '인간과 협력하는 지능형 로봇과 로봇 학습 알고리즘을 연구합니다.',
             json.dumps(['Python', 'ROS', 'PyTorch', 'Gazebo'], ensure_ascii=False)),
        ]
        
        for lab_data in research_labs_data:
            cursor.execute("""
                INSERT OR IGNORE INTO research_labs (director_id, name, name_en, location, phone, email, website, research_areas, keywords, description, tech_stack, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, lab_data)
        
        print(f"✅ {len(research_labs_data)}개의 연구실 추가 완료")
        
        # 4. 샘플 매칭 데이터 생성
        print("\n🔗 샘플 매칭 데이터 생성 중...")
        
        # 기존 프로젝트 중 일부에 대해 샘플 매칭 생성
        sample_matchings = [
            # AI 학습 도우미 프로젝트 (project_id: 6)과 AI 연구실들 매칭
            (6, 4, 0.85, 'AI와 패턴인식 전문성으로 교육 AI 시스템 개발에 적합', json.dumps({'tech_match': 0.9, 'domain_match': 0.8}, ensure_ascii=False)),
            (6, 14, 0.92, 'AI-빅데이터 연구센터의 풍부한 경험과 정부과제 수행 역량', json.dumps({'tech_match': 0.95, 'domain_match': 0.89}, ensure_ascii=False)),
            (6, 16, 0.75, '개인화 추천 시스템 기술을 교육 분야에 응용 가능', json.dumps({'tech_match': 0.8, 'domain_match': 0.7}, ensure_ascii=False)),
            
            # 스터디 매칭 플랫폼 (project_id: 2)과 관련 연구실들 매칭
            (2, 2, 0.78, '데이터베이스 전문성으로 사용자 매칭 시스템 구축', json.dumps({'tech_match': 0.8, 'domain_match': 0.76}, ensure_ascii=False)),
            (2, 12, 0.82, '그래프 기반 매칭 알고리즘 개발 경험', json.dumps({'tech_match': 0.85, 'domain_match': 0.79}, ensure_ascii=False)),
            
            # 세종 중고거래 마켓 (project_id: 3)과 보안/플랫폼 연구실 매칭
            (3, 8, 0.71, '안전한 거래를 위한 보안 시스템 구축', json.dumps({'tech_match': 0.7, 'domain_match': 0.72}, ensure_ascii=False)),
            (3, 13, 0.68, '사용자 개인정보 보호 기술 적용', json.dumps({'tech_match': 0.65, 'domain_match': 0.71}, ensure_ascii=False)),
        ]
        
        for matching_data in sample_matchings:
            cursor.execute("""
                INSERT OR IGNORE INTO project_lab_matchings (project_id, lab_id, similarity_score, matching_reason, matching_factors, status, created_at)
                VALUES (?, ?, ?, ?, ?, 'SUGGESTED', datetime('now'))
            """, matching_data)
        
        print(f"✅ {len(sample_matchings)}개의 샘플 매칭 데이터 생성 완료")
        
        # 커밋
        conn.commit()
        print("\n🎉 모든 연구실 데이터 및 매칭 시스템 설정이 완료되었습니다!")
        
        # 결과 요약 출력
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM professors")
        prof_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM research_labs")
        lab_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM project_lab_matchings")
        matching_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM projects WHERE is_active = 1")
        project_count = cursor.fetchone()[0]
        
        print(f"""
📊 세종 스타트업 네비게이터 + 연구실 매칭 시스템 현황:
   🏛️ 학과: {dept_count}개
   👨‍🏫 교수: {prof_count}명  
   🔬 연구실: {lab_count}개
   📁 활성 프로젝트: {project_count}개
   🔗 매칭 레코드: {matching_count}개
   
🌟 주요 기능:
   ✅ AI 기반 프로젝트-연구실 매칭
   ✅ 세종대 인공지능융합대학 연구실 데이터베이스
   ✅ 협력 연구 추천 시스템
   ✅ 매칭 이력 및 상태 관리
        """)
        
        print("\n🚀 사용법:")
        print("1. POST /research-labs/match-project - 프로젝트에 맞는 연구실 찾기")
        print("2. GET /research-labs/ - 연구실 목록 조회 및 검색")
        print("3. GET /research-labs/recommendations/{project_id} - 추천 연구실")
        print("4. PUT /research-labs/matching/{matching_id}/status - 매칭 상태 업데이트")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        
    finally:
        conn.close()

if __name__ == "__main__":
    insert_all_data()