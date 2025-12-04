"""
등락률 상위 자동화 - 메인 스크립트
============================================

사용법:
    python main_ranking.py

구글 시트 구조 (시트2):
    A열: 날짜 (사용 안함)
    B열: 재료
    C열: 종목명
    D열: 등락률(%)
    E열: 거래대금(백만)
    F열: 내용
"""

import os
import sys
from datetime import datetime

from sheet_reader_ranking import SheetReaderRanking
from html_renderer_ranking import HtmlRendererRanking


# ===== 설정 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "service_account.json.json")
SPREADSHEET_ID = "1dX8Diej7AQixm7fBrnrdUybxW2Au9QzyATYRBKZN_jk"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🚀 등락률 상위 자동화 시작")
    print("=" * 50)
    
    # 출력 폴더 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 데이터 가져오기
    print("\n📡 구글 시트 시트2에서 데이터 가져오는 중...")
    try:
        reader = SheetReaderRanking(CREDENTIALS_PATH, SPREADSHEET_ID)
        reader.connect()
        
        # 시트2의 모든 데이터 가져오기
        stocks = reader.get_ranking_data()
        
        if not stocks:
            print(f"⚠️ 시트2에 데이터가 없습니다!")
            return
        
        # 재료별 그룹화
        groups = reader.group_by_material(stocks)
        
        if not groups:
            print(f"⚠️ 그룹화할 데이터가 없습니다!")
            return
            
    except FileNotFoundError:
        print(f"❌ 서비스 계정 파일을 찾을 수 없습니다: {CREDENTIALS_PATH}")
        print("   service_account.json.json 파일을 프로젝트 폴더에 추가해주세요.")
        return
    except Exception as e:
        print(f"❌ 구글 시트 연결 실패: {e}")
        return
    
    print(f"\n📦 총 {len(groups)}개의 재료 그룹")
    print(f"📦 총 {sum(len(g.stocks) for g in groups)}개의 종목")
    
    # 이미지 생성 (HTML 기반)
    print("\n🎨 이미지 생성 중 (HTML → 스크린샷)...")
    renderer = HtmlRendererRanking(BASE_DIR)
    
    # 출력 파일명 (오늘 날짜 사용)
    today = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(OUTPUT_DIR, f"등락률상위_{today}")
    
    # 생성 실행
    output_files = renderer.generate(groups, output_path)
    
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

