"""
월클 답안지 자동화 - 메인 스크립트
============================================

사용법:
    python main_answersheet.py

Airtable 구조:
    종목명 (Single line text)
    핵심키워드 (Single line text)
    편입일 (Date)
    답안지유형 (Multiple select) - 시대흐름, 슈퍼픽, 일정매매
    상태 (Single select) - 관심, 보유자관점, 신규매수주의, 분할매도, 전략훼손
    국가 (Single select)
    대분류 (Single line text)
    소분류 (Single line text)
    핵심일정 (Single line text)
"""

import os
import sys
from datetime import datetime

from airtable_reader import AirtableReader
from html_renderer_answersheet import HtmlRendererAnswerSheet


# ===== 설정 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Airtable 설정 (환경변수 또는 config 파일에서 로드)
# 로컬 실행 시: config_airtable.py 파일 사용
# GitHub Actions: Secrets에서 환경변수로 주입
try:
    from config_airtable import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID
except ImportError:
    AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "")
    AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "appA4t9o1QMTDZul7")
    AIRTABLE_TABLE_ID = os.environ.get("AIRTABLE_TABLE_ID", "tbllRbqwpfEY8dV2O")


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🚀 월클 답안지 자동화 시작")
    print("=" * 50)
    
    # 출력 폴더 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 데이터 가져오기
    print("\n📡 Airtable에서 데이터 가져오는 중...")
    try:
        reader = AirtableReader(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
        reader.connect()
        
        # 유형별로 그룹화된 데이터 가져오기
        data = reader.get_grouped_data()
        
        if not data:
            print(f"⚠️ 데이터가 없습니다!")
            return
        
        # 데이터 요약
        시대흐름_count = sum(
            len(cat.종목들) 
            for country in data.get('시대흐름', []) 
            for cat in country.카테고리들
        )
        슈퍼픽_count = len(data.get('슈퍼픽', []))
        일정매매_count = len(data.get('일정매매', []))
        
        total_count = 시대흐름_count + 슈퍼픽_count + 일정매매_count
        
        if total_count == 0:
            print(f"⚠️ 표시할 종목이 없습니다!")
            return
            
    except Exception as e:
        print(f"❌ Airtable 연결 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n📦 총 {total_count}개의 종목")
    
    # 이미지 생성 (HTML 기반)
    print("\n🎨 이미지 생성 중 (HTML → 스크린샷)...")
    renderer = HtmlRendererAnswerSheet(BASE_DIR)
    
    # 출력 파일명 (오늘 날짜 사용)
    today = datetime.now().strftime("%Y%m%d")
    today_display = datetime.now().strftime("%Y.%m.%d")
    output_path = os.path.join(OUTPUT_DIR, f"답안지_{today}")
    
    # 생성 실행
    output_files = renderer.generate(data, today_display, output_path)
    
    # 완료 메시지
    print("\n" + "=" * 50)
    print("✅ 이미지 생성 완료!")
    print("=" * 50)
    for f in output_files:
        print(f"   📁 {f}")
    print("\n")
    
    return output_files


if __name__ == "__main__":
    main()

