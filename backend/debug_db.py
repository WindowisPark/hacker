# backend/debug_db.py
"""
데이터베이스 상태 진단 스크립트
"""
import sqlite3
import json

def debug_database():
    """데이터베이스 상태 확인"""
    try:
        conn = sqlite3.connect('sejong_startup.db')
        cursor = conn.cursor()
        
        print("🔍 데이터베이스 진단을 시작합니다...\n")
        
        # 1. 테이블 존재 여부 확인
        print("📋 테이블 목록:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        print()
        
        # 2. 각 테이블별 데이터 개수 확인
        print("📊 테이블별 데이터 개수:")
        table_counts = {}
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_counts[table_name] = count
                print(f"  - {table_name}: {count}개")
            except Exception as e:
                print(f"  - {table_name}: 오류 ({e})")
        print()
        
        # 3. 연구실 관련 테이블 상세 확인
        if 'research_labs' in [t[0] for t in tables]:
            print("🔬 연구실 테이블 상세:")
            cursor.execute("SELECT lab_id, name, director_id, is_active FROM research_labs LIMIT 5")
            labs = cursor.fetchall()
            for lab in labs:
                print(f"  - ID: {lab[0]}, 이름: {lab[1]}, 지도교수ID: {lab[2]}, 활성: {lab[3]}")
            print()
        else:
            print("❌ research_labs 테이블이 없습니다!")
        
        if 'departments' in [t[0] for t in tables]:
            print("🏛️ 학과 테이블 상세:")
            cursor.execute("SELECT department_id, name FROM departments")
            depts = cursor.fetchall()
            for dept in depts:
                print(f"  - ID: {dept[0]}, 이름: {dept[1]}")
            print()
        else:
            print("❌ departments 테이블이 없습니다!")
        
        if 'professors' in [t[0] for t in tables]:
            print("👨‍🏫 교수 테이블 상세:")
            cursor.execute("SELECT professor_id, name, department_id, is_active FROM professors LIMIT 5")
            profs = cursor.fetchall()
            for prof in profs:
                print(f"  - ID: {prof[0]}, 이름: {prof[1]}, 학과ID: {prof[2]}, 활성: {prof[3]}")
            print()
        else:
            print("❌ professors 테이블이 없습니다!")
        
        # 4. JOIN 쿼리 테스트 (API에서 사용하는 것과 동일)
        print("🔗 JOIN 쿼리 테스트:")
        try:
            cursor.execute("""
                SELECT rl.lab_id, rl.name, rl.is_active, p.name as prof_name, d.name as dept_name
                FROM research_labs rl
                LEFT JOIN professors p ON rl.director_id = p.professor_id
                LEFT JOIN departments d ON p.department_id = d.department_id
                WHERE rl.is_active = 1
                LIMIT 3
            """)
            results = cursor.fetchall()
            print(f"  JOIN 결과: {len(results)}개")
            for result in results:
                print(f"    - {result}")
        except Exception as e:
            print(f"  JOIN 쿼리 오류: {e}")
        print()
        
        # 5. 테이블 스키마 확인
        print("📐 research_labs 테이블 스키마:")
        if 'research_labs' in [t[0] for t in tables]:
            cursor.execute("PRAGMA table_info(research_labs)")
            schema = cursor.fetchall()
            for col in schema:
                print(f"  - {col[1]} ({col[2]}) - NOT NULL: {col[3]}, DEFAULT: {col[4]}")
        
        print("\n" + "="*50)
        print("📈 요약:")
        print(f"  - 총 테이블 수: {len(tables)}")
        for table_name, count in table_counts.items():
            if count == 0:
                print(f"  ⚠️  {table_name}: 데이터 없음")
            else:
                print(f"  ✅ {table_name}: {count}개")
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 오류: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def check_specific_queries():
    """API에서 사용하는 특정 쿼리들 테스트"""
    try:
        conn = sqlite3.connect('sejong_startup.db')
        cursor = conn.cursor()
        
        print("\n🧪 API 쿼리 테스트:")
        
        # 1. 기본 연구실 조회 쿼리
        print("1. 기본 연구실 조회:")
        cursor.execute("SELECT * FROM research_labs WHERE is_active = 1")
        labs = cursor.fetchall()
        print(f"   결과: {len(labs)}개")
        
        # 2. 연구실-교수-학과 JOIN 쿼리
        print("2. 연구실-교수-학과 JOIN:")
        cursor.execute("""
            SELECT rl.lab_id, rl.name, p.name as prof_name, d.name as dept_name
            FROM research_labs rl
            JOIN professors p ON rl.director_id = p.professor_id
            JOIN departments d ON p.department_id = d.department_id
            WHERE rl.is_active = 1
        """)
        join_results = cursor.fetchall()
        print(f"   결과: {len(join_results)}개")
        
        if len(join_results) > 0:
            print("   샘플 데이터:")
            for i, result in enumerate(join_results[:3]):
                print(f"     {i+1}. {result}")
        
    except Exception as e:
        print(f"❌ 쿼리 테스트 오류: {e}")
    finally:
        conn.close()

def run_data_insertion():
    """데이터 삽입 스크립트 실행"""
    print("\n🚀 데이터 삽입을 시도합니다...")
    try:
        # integrated_data_setup.py의 내용을 여기서 실행
        from integrated_data_setup import insert_all_data
        insert_all_data()
        print("✅ 데이터 삽입 완료!")
    except ImportError:
        print("❌ integrated_data_setup.py 파일을 찾을 수 없습니다.")
        print("💡 backend/ 디렉토리에서 다음을 실행하세요:")
        print("   python integrated_data_setup.py")
    except Exception as e:
        print(f"❌ 데이터 삽입 오류: {e}")

if __name__ == "__main__":
    debug_database()
    check_specific_queries()
    
    # 데이터가 없다면 삽입 제안
    conn = sqlite3.connect('sejong_startup.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM research_labs WHERE is_active = 1")
        lab_count = cursor.fetchone()[0]
        if lab_count == 0:
            print("\n💡 연구실 데이터가 없습니다. 데이터를 삽입하시겠습니까?")
            response = input("데이터 삽입하기 (y/n): ")
            if response.lower() == 'y':
                run_data_insertion()
    except:
        print("\n💡 테이블이 없거나 데이터가 없습니다. 데이터 설정이 필요합니다.")
    finally:
        conn.close()