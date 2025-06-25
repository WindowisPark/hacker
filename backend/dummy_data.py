# dummy_data.py - 세종 스타트업 네비게이터 더미 데이터 삽입 스크립트

import sqlite3
import json
from datetime import datetime, timedelta

def insert_dummy_data():
    # 데이터베이스 연결
    conn = sqlite3.connect('sejong_startup.db')
    cursor = conn.cursor()
    
    try:
        print("🚀 더미 데이터 삽입을 시작합니다...")
        
        # 1. 사용자 데이터 추가 (user_id 3번부터)
        print("\n👥 사용자 데이터 추가 중...")
        users_data = [
            # DREAMER (아이디어 제공자)
            ('dreamer1@sejong.ac.kr', '$2b$12$LQv3c1yqBwlVHpPjrPHXlOes8z9FyOhRD1PKE.Kq9wHdCnW5.2Kue', '김아이디어', '경영학과', 2, 'DREAMER', '창의적인 아이디어로 세상을 바꾸고 싶습니다', '22011001'),
            ('dreamer2@sejong.ac.kr', '$2b$12$LQv3c1yqBwlVHpPjrPHXlOes8z9FyOhRD1PKE.Kq9wHdCnW5.2Kue', '박창업', '경제학과', 3, 'DREAMER', '스타트업에 관심이 많은 학생입니다', '21021002'),
            ('design@sejong.ac.kr', '$2b$12$LQv3c1yqBwlVHpPjrPHXlOes8z9FyOhRD1PKE.Kq9wHdCnW5.2Kue', '이비전', '산업디자인학과', 4, 'DREAMER', '디자인 씽킹으로 문제를 해결합니다', '20031003'),
            
            # BUILDER (실행자)
            ('builder2@sejong.ac.kr', '$2b$12$LQv3c1yqBwlVHpPjrPHXlOes8z9FyOhRD1PKE.Kq9wHdCnW5.2Kue', '강프로젝트', '소프트웨어학과', 4, 'BUILDER', '팀을 이끄는 리더십이 있습니다', '20051002'),
            ('builder3@sejong.ac.kr', '$2b$12$LQv3c1yqBwlVHpPjrPHXlOes8z9FyOhRD1PKE.Kq9wHdCnW5.2Kue', '정개발', '전자정보통신공학과', 2, 'BUILDER', '풀스택 개발자를 꿈꿉니다', '22061003'),
            
            # SPECIALIST (전문가)
            ('frontend@sejong.ac.kr', '$2b$12$LQv3c1yqBwlVHpPjrPHXlOes8z9FyOhRD1PKE.Kq9wHdCnW5.2Kue', '김프론트', '컴퓨터공학과', 4, 'SPECIALIST', 'React와 TypeScript 전문가입니다', '20071001'),
            ('backend@sejong.ac.kr', '$2b$12$LQv3c1yqBwlVHpPjrPHXlOes8z9FyOhRD1PKE.Kq9wHdCnW5.2Kue', '이백엔드', '소프트웨어학과', 3, 'SPECIALIST', 'Python과 FastAPI로 견고한 백엔드를 만듭니다', '21081002'),
            ('design2@sejong.ac.kr', '$2b$12$LQv3c1yqBwlVHpPjrPHXlOes8z9FyOhRD1PKE.Kq9wHdCnW5.2Kue', '박디자인', '시각디자인학과', 2, 'SPECIALIST', 'UI/UX 디자인으로 사용자 경험을 개선합니다', '22091003'),
            ('data@sejong.ac.kr', '$2b$12$LQv3c1yqBwlVHpPjrPHXlOes8z9FyOhRD1PKE.Kq9wHdCnW5.2Kue', '최데이터', '데이터사이언스학과', 3, 'SPECIALIST', '데이터 분석과 AI 모델링이 전문입니다', '21101004'),
            ('marketing@sejong.ac.kr', '$2b$12$LQv3c1yqBwlVHpPjrPHXlOes8z9FyOhRD1PKE.Kq9wHdCnW5.2Kue', '강마케팅', '경영학과', 4, 'SPECIALIST', '디지털 마케팅 전략 수립이 특기입니다', '20111005')
        ]
        
        for i, user_data in enumerate(users_data):
            days_ago = 30 - i * 3  # 30일 전부터 3일씩 간격
            cursor.execute("""
                INSERT INTO users (email, password_hash, name, major, year, user_type, profile_info, sejong_student_id, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', ? || ' days'))
            """, user_data + (f'-{days_ago}',))
        
        print(f"✅ {len(users_data)}명의 사용자가 추가되었습니다.")
        
        # 2. 프로젝트 데이터 추가 (project_id 2번부터)
        print("\n📁 프로젝트 데이터 추가 중...")
        projects_data = [
            # (owner_id, name, description, idea_name, service_type, target_type, stage, is_active, is_public, days_ago)
            (3, '스터디 매칭 플랫폼', '같은 과목을 듣는 학생들의 스터디 그룹 매칭', '학습 커뮤니티', 'WEB', 'B2C', 'PROTOTYPE', 1, 1, 20),
            (4, '세종 중고거래 마켓', '세종대 학생들만 이용할 수 있는 안전한 중고거래', '캠퍼스 마켓플레이스', 'APP', 'B2C', 'MVP', 1, 1, 22),
            (4, '창업 아이디어 공유', '학생들의 창업 아이디어를 공유하고 피드백받는 플랫폼', '아이디어 허브', 'WEB', 'B2C', 'IDEA', 1, 0, 15),
            (5, '세종 이벤트 관리', '교내 행사와 동아리 활동을 한눈에 볼 수 있는 서비스', '캠퍼스 이벤트', 'APP', 'B2C', 'BETA', 1, 1, 18),
            (6, 'AI 학습 도우미', '개인 맞춤형 AI 학습 계획 및 진도 관리', 'EdTech 플랫폼', 'WEB', 'B2C', 'MVP', 1, 1, 16),
            (6, '팀 프로젝트 관리툴', '학과 팀 프로젝트를 효율적으로 관리하는 도구', '협업 도구', 'WEB', 'B2B', 'PROTOTYPE', 1, 1, 10),
            (7, '세종 헬스케어 앱', '학생들의 건강 관리를 도와주는 종합 헬스케어', '건강 관리', 'APP', 'B2C', 'IDEA', 1, 1, 12),
            (7, '세종 카풀 서비스', '통학하는 학생들을 위한 카풀 매칭 서비스', '교통 공유', 'APP', 'B2C', 'LAUNCH', 1, 1, 8)
        ]
        
        for project_data in projects_data:
            cursor.execute("""
                INSERT INTO projects (owner_id, name, description, idea_name, service_type, target_type, stage, is_active, is_public, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', ? || ' days'))
            """, project_data)
        
        print(f"✅ {len(projects_data)}개의 프로젝트가 추가되었습니다.")
        
        # 3. 이력서 데이터 추가
        print("\n📋 이력서 데이터 추가 중...")
        
        # 김프론트 이력서 (user_id 8)
        tech_stack_1 = json.dumps([
            {"name": "React", "level": "ADVANCED"},
            {"name": "TypeScript", "level": "ADVANCED"},
            {"name": "Next.js", "level": "INTERMEDIATE"},
            {"name": "Tailwind CSS", "level": "INTERMEDIATE"}
        ], ensure_ascii=False)
        
        work_exp_1 = json.dumps([
            {"company": "세종대학교 창업지원단", "position": "프론트엔드 개발 인턴", 
             "start_date": "2023-06", "end_date": "2023-12", 
             "description": "대학 창업지원 웹사이트 프론트엔드 개발"}
        ], ensure_ascii=False)
        
        awards_1 = json.dumps([
            {"title": "해커톤 최우수상", "organization": "세종대학교", 
             "date": "2023-11", "description": "교내 해커톤에서 혁신적인 UI/UX로 최우수상 수상"}
        ], ensure_ascii=False)
        
        links_1 = json.dumps([
            {"type": "GITHUB", "title": "GitHub", "url": "https://github.com/kimfront"},
            {"type": "PORTFOLIO", "title": "포트폴리오", "url": "https://kimfront.dev"}
        ], ensure_ascii=False)
        
        cursor.execute("""
            INSERT INTO resumes (user_id, introduction, tech_stack, work_experience, awards, external_links, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now', '-9 days'), datetime('now', '-3 days'))
        """, (8, '안녕하세요! 3년 경력의 프론트엔드 개발자입니다. 사용자 중심의 인터페이스 설계와 최신 기술 도입에 관심이 많습니다.',
              tech_stack_1, work_exp_1, awards_1, links_1))
        
        # 이백엔드 이력서 (user_id 9)
        tech_stack_2 = json.dumps([
            {"name": "Python", "level": "EXPERT"},
            {"name": "FastAPI", "level": "ADVANCED"},
            {"name": "PostgreSQL", "level": "ADVANCED"},
            {"name": "Docker", "level": "INTERMEDIATE"}
        ], ensure_ascii=False)
        
        work_exp_2 = json.dumps([
            {"company": "테크 스타트업", "position": "백엔드 개발자", 
             "start_date": "2023-03", "end_date": None, 
             "description": "FastAPI 기반 마이크로서비스 아키텍처 설계 및 개발"}
        ], ensure_ascii=False)
        
        awards_2 = json.dumps([
            {"title": "오픈소스 기여상", "organization": "KOSS", 
             "date": "2023-09", "description": "Python 오픈소스 프로젝트에 기여하여 수상"}
        ], ensure_ascii=False)
        
        links_2 = json.dumps([
            {"type": "GITHUB", "title": "GitHub", "url": "https://github.com/leebackend"},
            {"type": "BLOG", "title": "기술 블로그", "url": "https://leebackend.tistory.com"}
        ], ensure_ascii=False)
        
        cursor.execute("""
            INSERT INTO resumes (user_id, introduction, tech_stack, work_experience, awards, external_links, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now', '-7 days'), datetime('now', '-1 days'))
        """, (9, '견고하고 확장 가능한 백엔드 시스템 설계가 특기인 개발자입니다. 클린 아키텍처와 테스트 주도 개발을 지향합니다.',
              tech_stack_2, work_exp_2, awards_2, links_2))
        
        # 박디자인 이력서 (user_id 10)
        tech_stack_3 = json.dumps([
            {"name": "Figma", "level": "EXPERT"},
            {"name": "Adobe XD", "level": "ADVANCED"},
            {"name": "Photoshop", "level": "ADVANCED"},
            {"name": "Illustrator", "level": "INTERMEDIATE"}
        ], ensure_ascii=False)
        
        work_exp_3 = json.dumps([
            {"company": "디자인 에이전시", "position": "UI/UX 디자인 인턴", 
             "start_date": "2023-07", "end_date": "2023-12", 
             "description": "모바일 앱 UI/UX 디자인 및 사용자 테스트 진행"}
        ], ensure_ascii=False)
        
        awards_3 = json.dumps([
            {"title": "디자인 공모전 대상", "organization": "한국디자인학회", 
             "date": "2023-10", "description": "모바일 앱 디자인 부문에서 대상 수상"}
        ], ensure_ascii=False)
        
        links_3 = json.dumps([
            {"type": "PORTFOLIO", "title": "Behance", "url": "https://behance.net/parkdesign"},
            {"type": "BLOG", "title": "디자인 일기", "url": "https://parkdesign.notion.site"}
        ], ensure_ascii=False)
        
        cursor.execute("""
            INSERT INTO resumes (user_id, introduction, tech_stack, work_experience, awards, external_links, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now', '-5 days'), datetime('now', '-2 days'))
        """, (10, 'UI/UX 디자인을 통해 사용자에게 즐거운 경험을 선사하고 싶은 디자이너입니다. 사용자 리서치와 프로토타이핑이 특기입니다.',
              tech_stack_3, work_exp_3, awards_3, links_3))
        
        print("✅ 3개의 이력서가 추가되었습니다.")
        
        # 4. 팀원 모집 공고
        print("\n👥 팀원 모집 공고 추가 중...")
        openings_data = [
            # (project_id, role_name, description, required_skills, commitment_type, status, days_ago)
            (1, '프론트엔드 개발자', 'React Native로 음식 배달 앱을 개발할 프론트엔드 개발자를 찾습니다. UI/UX에 관심이 있으신 분 환영합니다.', 'React Native, JavaScript, UI/UX 감각', 'PART_TIME', 'OPEN', 26),
            (1, 'UI/UX 디자이너', '음식 배달 앱의 사용자 경험을 설계할 디자이너를 찾습니다. 모바일 앱 디자인 경험이 있으시면 좋습니다.', 'Figma, 모바일 UI/UX, 사용자 리서치', 'PART_TIME', 'OPEN', 25),
            (6, '백엔드 개발자', 'AI 모델과 연동되는 백엔드 API를 개발할 개발자를 찾습니다. 머신러닝에 관심이 있으시면 더욱 좋습니다.', 'Python, FastAPI, 머신러닝 기초', 'FULL_TIME', 'OPEN', 14),
            (6, '데이터 사이언티스트', '학습 패턴 분석과 개인화 알고리즘 개발을 담당할 데이터 사이언티스트를 찾습니다.', 'Python, TensorFlow, 데이터 분석', 'PART_TIME', 'OPEN', 13),
            (3, '풀스택 개발자', '중고거래 웹 플랫폼의 전반적인 개발을 함께할 풀스택 개발자를 찾습니다.', 'React, Node.js, 데이터베이스', 'FULL_TIME', 'OPEN', 20),
            (3, '마케팅 전문가', '서비스 런칭 후 마케팅 전략 수립과 실행을 담당할 분을 찾습니다.', '디지털 마케팅, SNS 마케팅, 기획', 'PART_TIME', 'OPEN', 18),
            (7, '프론트엔드 개발자', '협업 도구의 직관적인 인터페이스를 만들 프론트엔드 개발자를 찾습니다.', 'Vue.js, TypeScript, 협업 도구 이해', 'PART_TIME', 'OPEN', 8),
            (5, '모바일 개발자', '이벤트 관리 앱을 개발할 모바일 개발자를 찾습니다. Flutter 경험이 있으시면 좋습니다.', 'Flutter, Dart, 모바일 앱 개발', 'PART_TIME', 'CLOSED', 16),
            (8, 'UI/UX 디자이너', '헬스케어 앱의 사용자 친화적인 인터페이스를 디자인할 분을 찾습니다.', 'Figma, 헬스케어 도메인 이해, 모바일 UI', 'PART_TIME', 'OPEN', 10),
            (8, 'iOS 개발자', '네이티브 iOS 앱 개발을 담당할 개발자를 찾습니다.', 'Swift, UIKit, Core Data', 'FULL_TIME', 'OPEN', 9)
        ]
        
        for opening_data in openings_data:
            cursor.execute("""
                INSERT INTO team_openings (project_id, role_name, description, required_skills, commitment_type, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now', ? || ' days'))
            """, opening_data)
        
        print(f"✅ {len(openings_data)}개의 모집 공고가 추가되었습니다.")
        
        # 5. 팀 지원 현황
        print("\n🤝 팀 지원 현황 추가 중...")
        applications_data = [
            # (opening_id, applicant_id, message, portfolio_url, expected_commitment, available_hours, status, days_ago)
            (1, 8, '안녕하세요! React Native 경험이 3년 있고, 음식 배달 앱 개발에 관심이 많습니다. 사용자 경험을 중시하는 앱을 만들고 싶습니다.', 'https://github.com/kimfront/food-delivery-demo', 'PART_TIME', 25, 'PENDING', 24),
            (3, 8, 'FastAPI 백엔드 경험은 없지만 빠르게 학습하여 기여하고 싶습니다.', 'https://github.com/kimfront', 'PART_TIME', 20, 'PENDING', 12),
            (7, 8, 'Vue.js는 처음이지만 React 경험을 바탕으로 빠르게 적응할 수 있습니다.', 'https://kimfront.dev', 'PART_TIME', 15, 'ACCEPTED', 6),
            (3, 9, '백엔드 개발 3년 경력으로 안정적인 API 설계와 데이터베이스 최적화가 가능합니다. AI 모델 연동 경험도 있습니다.', 'https://github.com/leebackend/ai-learning-backend', 'FULL_TIME', 40, 'ACCEPTED', 13),
            (5, 9, '풀스택 개발 가능하며, 특히 백엔드 아키텍처 설계에 자신있습니다.', 'https://github.com/leebackend', 'FULL_TIME', 35, 'PENDING', 17),
            (2, 10, 'UI/UX 디자인 전공생으로 모바일 앱 디자인 경험이 풍부합니다. 사용자 리서치부터 프로토타이핑까지 가능합니다.', 'https://behance.net/parkdesign/food-app', 'PART_TIME', 20, 'ACCEPTED', 23),
            (9, 10, '헬스케어 도메인에 관심이 많고, 사용자 친화적인 건강 관리 앱을 만들고 싶습니다.', 'https://behance.net/parkdesign', 'PART_TIME', 18, 'PENDING', 8),
            (4, 11, '머신러닝과 데이터 분석 전문가입니다. 개인화 알고리즘 개발과 학습 패턴 분석에 특화되어 있습니다.', 'https://github.com/choiData/ai-learning-analysis', 'PART_TIME', 25, 'PENDING', 11),
            (6, 12, '디지털 마케팅 경력 2년으로 SNS 마케팅과 바이럴 전략에 특화되어 있습니다. 대학생 타겟 마케팅 경험이 풍부합니다.', 'https://portfolio.kangmarketing.com', 'PART_TIME', 20, 'REJECTED', 16)
        ]
        
        for app_data in applications_data:
            cursor.execute("""
                INSERT INTO team_applications (opening_id, applicant_id, message, portfolio_url, expected_commitment, available_hours, status, applied_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now', ? || ' days'))
            """, app_data)
        
        print(f"✅ {len(applications_data)}개의 지원서가 추가되었습니다.")
        
        # 6. 린 캔버스
        print("\n📊 린 캔버스 추가 중...")
        cursor.execute("""
            INSERT INTO lean_canvas (project_id, problem, customer_segments, unique_value_proposition, solution, unfair_advantage, revenue_streams, cost_structure, key_metrics, channels, canvas_version, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '-15 days'), datetime('now', '-10 days'))
        """, (6, '개별 학생의 학습 패턴과 이해도가 다른데 획일적인 교육과정으로 인한 학습 효율성 저하',
              '대학생, 고등학생, 자기주도학습을 원하는 학습자',
              'AI 기반 개인 맞춤형 학습 계획과 실시간 진도 관리',
              'AI 학습 분석 알고리즘 개발, 개인화된 학습 경로 제공',
              '세종대 컴공과 AI 연구 자원과 학습 데이터 접근성',
              '구독료, 프리미엄 기능, 교육기관 라이선스',
              'AI 모델 개발비, 서버 비용, 콘텐츠 제작비',
              '학습 완료율, 성적 향상도, 일 사용시간',
              '교육 플랫폼 파트너십, 학교 제휴, 온라인 광고', 1))
        
        print("✅ 1개의 린 캔버스가 추가되었습니다.")
        
        # 7. AI 보고서
        print("\n🤖 AI 보고서 추가 중...")
        idea_info = json.dumps({"idea_name": "AI 학습 도우미", "industry": "에듀테크", "target_market": "대학생 및 수험생"}, ensure_ascii=False)
        existing_services = json.dumps({"name": ["Khan Academy", "Coursera", "뤼이드"], "business_model": ["구독료", "콘텐츠 판매", "기업 라이선스"], "marketing": ["학교 제휴", "무료 체험", "성과 기반 마케팅"]}, ensure_ascii=False)
        service_limitations = '기존 서비스들은 개인화 수준이 낮고, 한국 교육과정에 특화되지 않음'
        lean_canvas_detailed = json.dumps({"problem": "획일적 교육의 한계", "solution": "AI 기반 완전 개인화 학습", "market_size": "국내 사교육 시장 20조원"}, ensure_ascii=False)
        
        cursor.execute("""
            INSERT INTO ai_reports (project_id, requester_id, report_type, idea_info, existing_services, service_limitations, lean_canvas_detailed, confidence_score, generation_time_seconds, token_usage, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '-13 days'))
        """, (6, 6, 'LEAN_CANVAS', idea_info, existing_services, service_limitations, lean_canvas_detailed, 0.92, 52, 2890, 'COMPLETED'))
        
        print("✅ 1개의 AI 보고서가 추가되었습니다.")
        
        # 커밋
        conn.commit()
        print("\n🎉 모든 더미 데이터 삽입이 완료되었습니다!")
        
        # 결과 요약 출력
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM resumes")
        resume_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM team_openings")
        opening_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM team_applications")
        application_count = cursor.fetchone()[0]
        
        print(f"""
📈 현재 데이터베이스 현황:
   👥 사용자: {user_count}명
   📁 프로젝트: {project_count}개
   📋 이력서: {resume_count}개
   👔 모집공고: {opening_count}개
   🤝 지원서: {application_count}개
   📊 린 캔버스: 1개
   🤖 AI 보고서: 1개
        """)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
        import traceback
        traceback.print_exc()
        
    finally:
        conn.close()

if __name__ == "__main__":
    insert_dummy_data()