# backend/lab_data_parser.py
import sqlite3
import json
import re
from datetime import datetime

def parse_and_insert_lab_data():
    """
    세종대학교 연구실 데이터를 파싱하여 데이터베이스에 삽입
    """
    # 데이터베이스 연결
    conn = sqlite3.connect('sejong_startup.db')
    cursor = conn.cursor()
    
    try:
        print("🔬 세종대학교 연구실 데이터 삽입을 시작합니다...")
        
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
                INSERT INTO departments (name, name_en, college, building, description, created_at)
                VALUES (?, ?, '인공지능융합대학', ?, ?, datetime('now'))
            """, dept_data)
        
        print(f"✅ {len(departments_data)}개 학과가 추가되었습니다.")
        
        # 2. 교수 데이터 삽입
        print("\n👨‍🏫 교수 데이터 추가 중...")
        professors_data = [
            # 컴퓨터공학과
            (1, '박태순', 'Taesoon Park', '교수', None, '02-3408-3240', '대양AI센터 823호', '분산처리시스템'),
            (1, '신동일', 'Dongil Shin', '교수', None, '02-3408-3241', '대양AI센터 825호', '데이터베이스'),
            (1, '이강원', 'Kangwon Lee', '교수', None, '02-3408-3489', '집현관 910호', 'Networks, Cloud, AI & Data, Smart Factory'),
            (1, '신동규', 'Donggyu Shin', '교수', None, '02-3408-3242', '대양AI센터 826호', '멀티미디어'),
            (1, '김원일', 'Wonil Kim', '교수', None, '02-3408-2902', '대양AI센터 804호', '데이터마이닝'),
            (1, '이영렬', 'Youngryol Lee', '교수', None, '02-3408-3753', '대양AI센터 821호', '영상처리'),
            (1, '문현준', 'Hyunjun Moon', '교수', None, '02-3408-3874', '대양AI센터 819호', '인공지능, 패턴인식'),
            (1, '한동일', 'Dongil Han', '교수', None, '02-3408-3751', '대양AI센터 721호', 'Computer Vision'),
            (1, '최수미', 'Sumi Choi', '교수', None, '02-3408-3754', '대양AI센터 720호', '컴퓨터그래픽스'),
            (1, '박우찬', 'Woochan Park', '교수', None, '02-3408-3752', '대양AI센터 723호', '컴퓨터구조론'),
            (1, '양효식', 'Hyosik Yang', '교수', None, '02-3408-3840', '대양AI센터 808호', '정보통신'),
            (1, '박기호', 'Kiho Park', '교수', None, '02-3408-3886', '대양AI센터 822호', '컴퓨터구조론, 임베디드시스템'),
            (1, '이수정', 'Sujeong Lee', '조교수', None, '02-6935-2480', '대양AI센터 423호', '정보통신, 컴퓨터공학'),
            (1, 'Dilshad Naqqash', 'Dilshad Naqqash', '조교수', None, None, '영실관 315-B호', 'Computer Vision, AI, Deep Learning, IoT'),
            (1, 'Usman Ali', 'Usman Ali', '조교수', None, '02-6935-2557', '영실관 315-B호', 'Computer Vision'),
            
            # 정보보호학과
            (2, '이종혁', 'Jonghyouk Lee', '부교수', 'jonghyouk@sejong.ac.kr', '02-3408-1846', '대양AI센터 803호', '사이버보안, 프로토콜 분석, 오펜시브 보안'),
            (2, '신지선', 'Jiseon Shin', '부교수', 'jsshin@sejong.ac.kr', '02-3408-3888', '대양AI센터 708호', '컴퓨터과학, 암호학, 인증, 드론/AI/블록체인 보안'),
            (2, '송재승', 'Jaeseung Song', '교수', 'jssong@sejong.ac.kr', '02-3408-2901', '대양AI센터 702호', '소프트웨어공학, 소프트웨어 검증, IoT 보안'),
            (2, '김영갑', 'Younggab Kim', '교수', 'alwaysgabi@sejong.ac.kr', '02-6935-2424', '대양AI센터 701호', '시스템보안, 보안공학, IoT/AI 영상/DB 보안'),
            (2, '윤주범', 'Jubeom Yun', '부교수', 'jbyun@sejong.ac.kr', '02-6935-2425', '대양AI센터 724호', '정보보호, 네트워크보안'),
            (2, '이광수', 'Kwangsu Lee', '부교수', 'kwangsu@sejong.ac.kr', '02-6935-2454', '대양AI센터 726호', '암호학, 공개키암호'),
            (2, '박기웅', 'Kiwoong Park', '교수', 'woongbak@sejong.ac.kr', '02-6935-2453', '대양AI센터 703호', '정보보호, 시스템보안'),
            (2, '김종현', 'Jonghyun Kim', '교수', 'jhk@sejong.ac.kr', '02-3408-3712', '충무관 407A호', '네트워크, 이동통신보안'),
            (2, 'Lewis Nkenyereye', 'Lewis Nkenyereye', '조교수', 'nkenyele@sejong.ac.kr', '02-6935-2436', '대양AI센터 457호', 'Information Security'),
            
            # 콘텐츠소프트웨어학과
            (3, '권순일', 'Sunil Kwon', '교수', 'sikwon@sejong.ac.kr', '02-3408-3847', '대양AI센터 624호', 'Speech & Audio Processing'),
            (3, '백성욱', 'Seongwook Baik', '교수', 'sbaik@sejong.ac.kr', '02-3408-3797', '대양AI센터 622호', '컴퓨터 비전, 데이터/비주얼 마이닝, 문화재 복원'),
            (3, '이종원', 'Jongwon Lee', '교수', 'jwlee@sejong.ac.kr', '02-3408-3798', '대양AI센터 619호', 'Augmented Reality, 3차원 공간 상호작용'),
            (3, '송오영', 'Oyoung Song', '교수', 'oysong@sejong.ac.kr', '02-3408-3830', '대양AI센터 625호', '컴퓨터 그래픽스'),
            (3, '최준연', 'Junyeon Choi', '교수', 'zoon@sejong.ac.kr', '02-3408-3887', '대양AI센터 620호', '정보시스템'),
            (3, '박상일', 'Sangil Park', '조교수', 'sipark@sejong.ac.kr', '02-3408-3832', '대양AI센터 626호', '컴퓨터 그래픽스'),
            (3, '변재욱', 'Jaeuk Byun', '조교수', 'jwbyun@sejong.ac.kr', '02-3408-1847', '대양AI센터 604호', '데이터마이닝, 사물인터넷, Temporal Graph'),
            (3, '이은상', 'Eunsang Lee', '조교수', 'eslee3209@sejong.ac.kr', '02-3408-2975', '대양AI센터 621호', 'Privacy-preserving machine learning'),
            (3, '정승화', 'Seunghwa Jung', '조교수', None, '02-3408-3795', '대양AI센터 623호', 'Computer Vision, VR/AR'),
            (3, '백경준', 'Kyungjun Baek', '조교수', None, '02-3408-3281', '대양AI센터 504호', 'Computer Vision, 딥러닝'),
            
            # 인공지능데이터사이언스학과
            (4, '문연국', 'Yeonguk Moon', '부교수', None, '02-3408-2984', '광개토관 920B', '공간플랫폼, 감정AI'),
            (4, '유성준', 'Sungjun Yoo', '석좌교수', 'sjyoo@sejong.ac.kr', '02-3408-3755', '대양AI센터 719호', '인공지능'),
            (4, '구영현', 'Younghyun Koo', '조교수', None, '02-3408-3253', '대양AI센터 801호', '인공지능, 메타러닝'),
            (4, '김장겸', 'Janggyeom Kim', '조교수', None, '02-3408-3233', '대양AI센터 413A', '에너지 ICT'),
            (4, '김정현', 'Jeonghyun Kim', '부교수', None, '02-3408-3238', '대양AI센터 507호', '지능형시스템'),
            (4, '민병석', 'Byungseok Min', '부교수', None, '02-3408-3348', '대양AI센터 501호', '컴퓨터비전, Industrial AI'),
            (4, '박동현', 'Donghyun Park', '조교수', None, '02-3408-1946', '대양AI센터 707호', '데이터마이닝, 음식인공지능응용'),
            (4, '신승협', 'Seunghyup Shin', '조교수', None, '02-3408-3252', '대양AI센터 310A', '기계/시스템 AI'),
            (4, '심태용', 'Taeyong Shim', '조교수', None, '02-3408-1886', '대양AI센터 518호', 'Generative AI, Biomedical Engineering, Protein Structure Prediction'),
            (4, '이동훈', 'Donghoon Lee', '조교수', None, '02-3408-3738', '다산관 411호', '자율주행, 모빌리티, 교통안전'),
            (4, '이수진', 'Sujin Lee', '조교수', None, '02-3408-1867', '대양AI센터 425호', '컴퓨터비전, HCI, 인공지능응용(예술, 엔터테인먼트)'),
            (4, '최우석', 'Wooseok Choi', '조교수', 'wschoi@sejong.ac.kr', None, None, '기후환경, 데이터사이언스, 디지털트윈, 머신러닝'),
            
            # AI로봇학과 주요 교수진 (일부)
            (5, '임유승', 'Yuseung Lim', '교수', None, None, None, '지능형 반도체, 뉴로모픽 소자, 전력반도체, 바이오센서'),
            (5, '김형석', 'Hyungseok Kim', '교수', 'hyungkim@sejong.ac.kr', None, None, '지능형 임베디드 시스템, 웨어러블 센서, VR, AI 시스템'),
            (5, '송진우', 'Jinwoo Song', '교수', 'jwsong@sejong.ac.kr', None, None, '무인 시스템을 위한 지능형 항법, 유도, 제어'),
            (5, '서재규', 'Jaekyu Suhr', '교수', 'jksuhr@sejong.ac.kr', None, None, '지능형 이동체 인식 시스템, 자율주행차 인식'),
            (5, '최유경', 'Yukyung Choi', '교수', 'ykchoi@sejong.ac.kr', None, None, '자율 지능 시스템을 위한 컴퓨터 비전 및 머신러닝'),
            (5, '강병현', 'Byunghyun Kang', '교수', 'brianbkang@sejong.ac.kr', None, None, '인간 친화 로봇, 로봇 학습 알고리즘'),
        ]
        
        for prof_data in professors_data:
            cursor.execute("""
                INSERT INTO professors (department_id, name, name_en, position, email, phone, office_location, research_fields, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, prof_data)
        
        print(f"✅ {len(professors_data)}명의 교수가 추가되었습니다.")
        
        # 3. 연구실 데이터 삽입
        print("\n🔬 연구실 데이터 추가 중...")
        research_labs_data = [
            # 컴퓨터공학과 연구실
            (1, '분산처리시스템 연구실', 'Distributed Processing Systems Lab', '대양AI센터 823호', None, None, None,
             json.dumps(['분산시스템', '클라우드컴퓨팅', '병렬처리'], ensure_ascii=False),
             '분산처리,클라우드,병렬처리,고성능컴퓨팅',
             '대규모 분산 시스템의 성능 최적화와 신뢰성 향상을 연구합니다.',
             json.dumps(['Java', 'Python', 'Kubernetes', 'Docker'], ensure_ascii=False)),
            
            (2, '데이터베이스 연구실', 'Database Lab', '대양AI센터 825호', None, None, None,
             json.dumps(['데이터베이스시스템', 'DBMS', '빅데이터'], ensure_ascii=False),
             '데이터베이스,DBMS,빅데이터,데이터마이닝',
             '차세대 데이터베이스 시스템과 빅데이터 처리 기술을 연구합니다.',
             json.dumps(['SQL', 'NoSQL', 'Hadoop', 'Spark'], ensure_ascii=False)),
            
            (7, '인공지능-빅데이터 연구센터', 'AI & Big Data Research Center', '대양AI센터 819호', None, None, None,
             json.dumps(['인공지능', '머신러닝', '빅데이터', '패턴인식'], ensure_ascii=False),
             'AI,머신러닝,딥러닝,빅데이터,패턴인식,데이터분석',
             '인공지능과 빅데이터 기술을 활용한 지능형 시스템 개발을 연구합니다.',
             json.dumps(['Python', 'TensorFlow', 'PyTorch', 'Spark', 'R'], ensure_ascii=False)),
            
            (8, '컴퓨터비전 연구실', 'Computer Vision Lab', '대양AI센터 721호', None, None, None,
             json.dumps(['컴퓨터비전', '영상처리', '딥러닝'], ensure_ascii=False),
             '컴퓨터비전,영상처리,딥러닝,이미지분석,객체인식',
             '컴퓨터 비전과 영상 처리 기술을 통한 지능형 시각 시스템을 개발합니다.',
             json.dumps(['Python', 'OpenCV', 'TensorFlow', 'PyTorch'], ensure_ascii=False)),
            
            # 정보보호학과 연구실
            (16, '정보보호 연구실', 'Information Security Lab', '대양AI센터 708호', None, 'jsshin@sejong.ac.kr', None,
             json.dumps(['암호학', '인증기술', 'AI보안', '블록체인보안'], ensure_ascii=False),
             '암호학,인증,AI보안,블록체인,드론보안,사이버보안',
             'AI와 블록체인 시대의 새로운 보안 위협에 대응하는 기술을 연구합니다.',
             json.dumps(['Python', 'C++', 'Blockchain', 'AI/ML'], ensure_ascii=False)),
            
            (19, '보안공학 연구실', 'Security Engineering Lab', '대양AI센터 701호', None, 'alwaysgabi@sejong.ac.kr', None,
             json.dumps(['시스템보안', '보안공학', 'AI영상보안', 'IoT보안'], ensure_ascii=False),
             '시스템보안,보안공학,AI영상보안,IoT보안,CCTV보안',
             'AI 기반 영상 보안과 IoT 시스템 보안을 전문으로 연구합니다.',
             json.dumps(['Python', 'C/C++', 'AI/ML', 'IoT'], ensure_ascii=False)),
            
            # 콘텐츠소프트웨어학과 연구실
            (26, '지능형 미디어 연구실', 'Intelligent Media Lab', '대양AI센터 622호', None, 'sbaik@sejong.ac.kr', None,
             json.dumps(['컴퓨터비전', '데이터마이닝', '비주얼마이닝', '문화재복원'], ensure_ascii=False),
             '컴퓨터비전,데이터마이닝,비주얼마이닝,AI비디오,문화재복원',
             '인공지능 기반 비디오 요약과 문화재 복원 기술을 연구합니다.',
             json.dumps(['Python', 'OpenCV', 'TensorFlow', 'Unity'], ensure_ascii=False)),
            
            (27, 'Mixed Reality & Interaction Lab', 'Mixed Reality & Interaction Lab', '대양AI센터 619호', None, 'jwlee@sejong.ac.kr', None,
             json.dumps(['증강현실', '가상현실', '3D상호작용', 'HCI'], ensure_ascii=False),
             'AR,VR,MR,증강현실,가상현실,3D,HCI,상호작용',
             '모바일 기반 증강현실과 3차원 공간 상호작용 기술을 연구합니다.',
             json.dumps(['Unity', 'C#', 'ARCore', 'ARKit', 'OpenGL'], ensure_ascii=False)),
            
            (31, 'Data Frameworks and Platforms Lab', 'DFPL', '대양AI센터 604호', None, 'jwbyun@sejong.ac.kr', None,
             json.dumps(['데이터마이닝', 'IoT', 'TemporalGraph', '그래프신경망'], ensure_ascii=False),
             '데이터마이닝,IoT,시간그래프,그래프신경망,GNN,데이터플랫폼',
             '시간에 따라 변화하는 그래프 데이터 처리 프레임워크를 연구합니다.',
             json.dumps(['Python', 'NetworkX', 'PyTorch Geometric', 'Neo4j'], ensure_ascii=False)),
            
            (32, '프라이버시보호 AI 연구실', 'Privacy-Preserving AI Lab', '대양AI센터 621호', None, 'eslee3209@sejong.ac.kr', None,
             json.dumps(['프라이버시보호ML', '연합학습', '차분프라이버시'], ensure_ascii=False),
             '프라이버시,연합학습,차분프라이버시,보안AI,개인정보보호',
             '개인정보를 보호하면서 AI 모델을 학습하는 기술을 연구합니다.',
             json.dumps(['Python', 'TensorFlow', 'PySyft', 'Opacus'], ensure_ascii=False)),
            
            # 인공지능데이터사이언스학과 연구실
            (37, 'FNAI Lab', 'Food & AI Lab', '대양AI센터 707호', None, None, None,
             json.dumps(['음식정보학', 'NLP', '추천시스템', '레시피생성'], ensure_ascii=False),
             '음식AI,음식정보학,NLP,추천시스템,레시피,요리',
             '자연어 처리를 활용한 개인화 음식 추천과 레시피 생성을 연구합니다.',
             json.dumps(['Python', 'BERT', 'GPT', 'Recommendation Systems'], ensure_ascii=False)),
            
            (42, '생성AI 및 바이오메디컬 연구실', 'Generative AI & Biomedical Lab', '대양AI센터 518호', None, None, None,
             json.dumps(['생성AI', '바이오메디컬', '단백질구조예측'], ensure_ascii=False),
             '생성AI,바이오메디컬,단백질,구조예측,신약개발,의료AI',
             '생성 AI를 활용한 단백질 구조 예측과 신약 개발을 연구합니다.',
             json.dumps(['Python', 'PyTorch', 'AlphaFold', 'RDKit'], ensure_ascii=False)),
            
            (46, '기후환경 데이터사이언스 연구실', 'Climate & Environmental Data Science Lab', None, None, 'wschoi@sejong.ac.kr', None,
             json.dumps(['기후환경', '데이터사이언스', '디지털트윈', '자연재해예측'], ensure_ascii=False),
             '기후,환경,데이터사이언스,디지털트윈,자연재해,기상예측',
             '빅데이터와 AI를 활용한 기후 변화와 자연재해 예측을 연구합니다.',
             json.dumps(['Python', 'R', 'TensorFlow', 'Climate Models'], ensure_ascii=False)),
            
            # AI로봇학과 연구실
            (47, 'Intelligent Semiconductor Laboratory', 'ISLab', None, None, None, None,
             json.dumps(['지능형반도체', '뉴로모픽', '전력반도체', '바이오센서'], ensure_ascii=False),
             '반도체,뉴로모픽,전력반도체,바이오센서,AI칩,저전력',
             '뉴로모픽 소자와 AI 전용 반도체를 개발합니다.',
             json.dumps(['VHDL', 'Verilog', 'SPICE', 'MATLAB'], ensure_ascii=False)),
            
            (50, 'Intelligent Navigation and Control Systems Lab', 'INCSL', None, None, 'jwsong@sejong.ac.kr', None,
             json.dumps(['지능항법', '제어시스템', '무인시스템', '센서융합'], ensure_ascii=False),
             '항법,제어,무인시스템,드론,자율주행,센서융합',
             '무인 시스템을 위한 지능형 항법과 제어 알고리즘을 연구합니다.',
             json.dumps(['MATLAB', 'Simulink', 'ROS', 'C++'], ensure_ascii=False)),
            
            (51, 'Intelligent Vehicle Perception Lab', 'IVPL', None, None, 'jksuhr@sejong.ac.kr', None,
             json.dumps(['자율주행', '차량인식', '컴퓨터비전', 'LIDAR'], ensure_ascii=False),
             '자율주행,차량인식,LIDAR,레이더,센서융합,객체인식',
             '자율주행차량의 환경 인식과 센서 융합 기술을 연구합니다.',
             json.dumps(['Python', 'C++', 'ROS', 'PCL', 'OpenCV'], ensure_ascii=False)),
            
            (53, 'Intelligent Robotics Lab', 'IRL', None, None, 'brianbkang@sejong.ac.kr', None,
             json.dumps(['지능로봇', '로봇학습', '인간로봇상호작용'], ensure_ascii=False),
             '지능로봇,로봇학습,HRI,인간로봇상호작용,협업로봇',
             '인간과 협력하는 지능형 로봇과 로봇 학습 알고리즘을 연구합니다.',
             json.dumps(['Python', 'ROS', 'PyTorch', 'Gazebo'], ensure_ascii=False)),
        ]
        
        for lab_data in research_labs_data:
            cursor.execute("""
                INSERT INTO research_labs (director_id, name, name_en, location, phone, email, website, research_areas, keywords, description, tech_stack, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, lab_data)
        
        print(f"✅ {len(research_labs_data)}개의 연구실이 추가되었습니다.")
        
        # 커밋
        conn.commit()
        print("\n🎉 모든 연구실 데이터 삽입이 완료되었습니다!")
        
        # 결과 요약 출력
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM professors")
        prof_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM research_labs")
        lab_count = cursor.fetchone()[0]
        
        print(f"""
📊 연구실 데이터베이스 현황:
   🏛️ 학과: {dept_count}개
   👨‍🏫 교수: {prof_count}명
   🔬 연구실: {lab_count}개
        """)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        
    finally:
        conn.close()

if __name__ == "__main__":
    parse_and_insert_lab_data()