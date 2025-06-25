# backend/update_emails.py
"""
교수 이메일 정보를 업데이트하는 스크립트
"""
import sqlite3

def update_professor_emails():
    """교수 이메일 정보 업데이트"""
    try:
        conn = sqlite3.connect('sejong_startup.db')
        cursor = conn.cursor()
        
        print("📧 교수 이메일 정보 업데이트를 시작합니다...")
        
        # 이메일 업데이트 데이터 (name, email)
        email_updates = [
            # 정보보호학과
            ('이종혁', 'jonghyouk@sejong.ac.kr'),
            ('신지선', 'jsshin@sejong.ac.kr'),
            ('송재승', 'jssong@sejong.ac.kr'),
            ('김영갑', 'alwaysgabi@sejong.ac.kr'),
            ('윤주범', 'jbyun@sejong.ac.kr'),
            ('이광수', 'kwangsu@sejong.ac.kr'),
            ('박기웅', 'woongbak@sejong.ac.kr'),
            ('김종현', 'jhk@sejong.ac.kr'),
            ('Lewis Nkenyereye', 'nkenyele@sejong.ac.kr'),
            
            # 콘텐츠소프트웨어학과
            ('권순일', 'sikwon@sejong.ac.kr'),
            ('백성욱', 'sbaik@sejong.ac.kr'),
            ('이종원', 'jwlee@sejong.ac.kr'),
            ('송오영', 'oysong@sejong.ac.kr'),
            ('최준연', 'zoon@sejong.ac.kr'),
            ('박상일', 'sipark@sejong.ac.kr'),
            ('변재욱', 'jwbyun@sejong.ac.kr'),
            ('이은상', 'eslee3209@sejong.ac.kr'),
            
            # 인공지능데이터사이언스학과
            ('유성준', 'sjyoo@sejong.ac.kr'),
            ('최우석', 'wschoi@sejong.ac.kr'),
            
            # AI로봇학과
            ('김형석', 'hyungkim@sejong.ac.kr'),
            ('송진우', 'jwsong@sejong.ac.kr'),
            ('서재규', 'jksuhr@sejong.ac.kr'),
            ('최유경', 'ykchoi@sejong.ac.kr'),
            ('강병현', 'brianbkang@sejong.ac.kr'),
        ]
        
        updated_count = 0
        for name, email in email_updates:
            cursor.execute("""
                UPDATE professors 
                SET email = ? 
                WHERE name = ? AND email IS NULL
            """, (email, name))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"   ✅ {name}: {email}")
        
        # 연구실 이메일도 업데이트 (연구실명, 이메일)
        lab_email_updates = [
            ('정보보호 연구실', 'jsshin@sejong.ac.kr'),
            ('보안공학 연구실', 'alwaysgabi@sejong.ac.kr'),
            ('지능형 미디어 연구실', 'sbaik@sejong.ac.kr'),
            ('Mixed Reality & Interaction Lab', 'jwlee@sejong.ac.kr'),
            ('Data Frameworks and Platforms Lab', 'jwbyun@sejong.ac.kr'),
            ('프라이버시보호 AI 연구실', 'eslee3209@sejong.ac.kr'),
            ('AI-빅데이터 연구센터', 'sjyoo@sejong.ac.kr'),
            ('기후환경 데이터사이언스 연구실', 'wschoi@sejong.ac.kr'),
            ('Intelligent Navigation and Control Systems Lab', 'jwsong@sejong.ac.kr'),
            ('Intelligent Vehicle Perception Lab', 'jksuhr@sejong.ac.kr'),
            ('Intelligent Robotics Lab', 'brianbkang@sejong.ac.kr'),
        ]
        
        lab_updated_count = 0
        for lab_name, email in lab_email_updates:
            cursor.execute("""
                UPDATE research_labs 
                SET email = ? 
                WHERE name = ? AND email IS NULL
            """, (email, lab_name))
            
            if cursor.rowcount > 0:
                lab_updated_count += 1
                print(f"   🔬 {lab_name}: {email}")
        
        conn.commit()
        print(f"\n✅ 업데이트 완료!")
        print(f"   - 교수 이메일: {updated_count}개")
        print(f"   - 연구실 이메일: {lab_updated_count}개")
        
        # 결과 확인
        print(f"\n📊 현재 이메일 보유 현황:")
        cursor.execute("SELECT COUNT(*) FROM professors WHERE email IS NOT NULL")
        prof_with_email = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM professors")
        total_profs = cursor.fetchone()[0]
        print(f"   - 교수: {prof_with_email}/{total_profs}명")
        
        cursor.execute("SELECT COUNT(*) FROM research_labs WHERE email IS NOT NULL")
        lab_with_email = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM research_labs")
        total_labs = cursor.fetchone()[0]
        print(f"   - 연구실: {lab_with_email}/{total_labs}개")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    update_professor_emails()