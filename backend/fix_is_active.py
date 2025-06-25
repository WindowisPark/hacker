# backend/fix_is_active.py
"""
is_active 필드를 NULL에서 1로 수정하는 스크립트
"""
import sqlite3

def fix_is_active_fields():
    """is_active 필드가 NULL인 것들을 1(True)로 수정"""
    try:
        conn = sqlite3.connect('sejong_startup.db')
        cursor = conn.cursor()
        
        print("🔧 is_active 필드 수정을 시작합니다...")
        
        # 1. research_labs 테이블 수정
        print("\n🔬 research_labs 테이블 수정 중...")
        cursor.execute("UPDATE research_labs SET is_active = 1 WHERE is_active IS NULL")
        research_labs_updated = cursor.rowcount
        print(f"   - {research_labs_updated}개 연구실의 is_active를 1로 설정")
        
        # 2. professors 테이블 수정
        print("\n👨‍🏫 professors 테이블 수정 중...")
        cursor.execute("UPDATE professors SET is_active = 1 WHERE is_active IS NULL")
        professors_updated = cursor.rowcount
        print(f"   - {professors_updated}명 교수의 is_active를 1로 설정")
        
        # 3. 결과 확인
        print("\n📊 수정 결과 확인:")
        
        cursor.execute("SELECT COUNT(*) FROM research_labs WHERE is_active = 1")
        active_labs = cursor.fetchone()[0]
        print(f"   - 활성 연구실: {active_labs}개")
        
        cursor.execute("SELECT COUNT(*) FROM professors WHERE is_active = 1")
        active_profs = cursor.fetchone()[0]
        print(f"   - 활성 교수: {active_profs}명")
        
        # 4. JOIN 테스트
        print("\n🔗 JOIN 쿼리 테스트:")
        cursor.execute("""
            SELECT COUNT(*)
            FROM research_labs rl
            JOIN professors p ON rl.director_id = p.professor_id
            JOIN departments d ON p.department_id = d.department_id
            WHERE rl.is_active = 1
        """)
        join_count = cursor.fetchone()[0]
        print(f"   - JOIN 결과: {join_count}개")
        
        # 5. 학과별 연구실 수 확인
        print("\n🏛️ 학과별 연구실 수:")
        cursor.execute("""
            SELECT d.name, COUNT(rl.lab_id) as lab_count
            FROM departments d
            LEFT JOIN professors p ON d.department_id = p.department_id
            LEFT JOIN research_labs rl ON p.professor_id = rl.director_id AND rl.is_active = 1
            GROUP BY d.department_id, d.name
            HAVING lab_count > 0
            ORDER BY lab_count DESC
        """)
        dept_labs = cursor.fetchall()
        for dept_name, count in dept_labs:
            print(f"   - {dept_name}: {count}개")
        
        # 커밋
        conn.commit()
        print("\n✅ 모든 수정이 완료되었습니다!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_is_active_fields()