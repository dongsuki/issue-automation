"""
장중 강세테마 동향 자동화 - 메인 스크립트
============================================

사용법:
    python main_theme.py                    # 시트3 최신 날짜 데이터로 이미지 생성
    python main_theme.py --date 2025.12.03  # 특정 날짜 지정
    python main_theme.py --test             # 테스트 데이터로 실행

구글 시트 구조 (시트3):
    A열: 날짜
    B열: 타입 (테마/개별)
    C열: 그룹명
    D열: 종목명
    E열: 등락률
    F열: 거래대금
    G열: 이슈내용
"""

import os
import sys
import argparse
from datetime import datetime

from sheet_reader_theme import SheetReaderTheme, CardData, StockItem
from html_renderer_theme import HtmlRendererTheme


# ===== 설정 =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "service_account.json.json")
SPREADSHEET_ID = "1dX8Diej7AQixm7fBrnrdUybxW2Au9QzyATYRBKZN_jk"
OUTPUT_DIR = os.path.join(BASE_DIR, "output")


def create_test_data():
    """테스트용 더미 데이터 생성"""
    return [
        CardData(
            card_type='theme',
            group_name='건설',
            main_issue='정부 주택공급 정책 기대에 침체됐던 건설주 상승세 "꿈틀"',
            stocks=[
                StockItem('한신공영', '30%', '543억'),
                StockItem('동신건설', '29.31%', '321억'),
                StockItem('일성건설', '11.12%', '189억'),
                StockItem('KD', '18.67%', '234억'),
                StockItem('대우건설', '11.12%', '876억'),
            ]
        ),
        CardData(
            card_type='theme',
            group_name='고속터미널',
            main_issue='"고속터미널 재개발" 기대감에 "이 회사들" 또또 상한가',
            stocks=[
                StockItem('천일고속', '29.97%', '456억'),
                StockItem('대성산업', '29.93%', '389억'),
                StockItem('동양고속', '29.87%', '210억'),
                StockItem('신영와코루', '6.89%', '98억'),
                StockItem('신세계', '4.19%', '1,234억'),
            ]
        ),
        CardData(
            card_type='theme',
            group_name='로봇',
            main_issue='K-피지컬 AI, 3대 틈새 "로봇·센서·소프트웨어"',
            stocks=[
                StockItem('링크솔루션', '29.92%', '678억'),
                StockItem('스맥', '21.2%', '456억'),
                StockItem('케이쓰리아이', '17.28%', '1,345억'),
                StockItem('피앤에스로보틱스', '8.26%', '210억'),
                StockItem('로보스타', '7.73%', '189억'),
            ]
        ),
        CardData(
            card_type='theme',
            group_name='바이오',
            main_issue='바이오주 사들이는 큰손들… 기술이전 기대감 솔솔',
            stocks=[
                StockItem('삼성에피스홀딩스', '24.21%', '1,789억'),
                StockItem('엘앤케이바이오', '17.29%', '321억'),
                StockItem('지놈앤컴퍼니', '17.29%', '245억'),
                StockItem('와이투솔루션', '14.89%', '167억'),
                StockItem('인벤티지랩', '11.06%', '123억'),
            ]
        ),
        CardData(
            card_type='theme',
            group_name='원전',
            main_issue='美 "한일 대미투자 원전부터" 발언에… 원전주, 동반 강세',
            stocks=[
                StockItem('우양에이치씨', '14.89%', '345억'),
                StockItem('일진파워', '9.27%', '567억'),
                StockItem('우진', '8.84%', '234억'),
                StockItem('태웅', '7.51%', '456억'),
                StockItem('현대건설', '6.98%', '1,567억'),
            ]
        ),
        CardData(
            card_type='theme',
            group_name='방산',
            main_issue='KAI, 이집트 방산전시회 참가… 아프리카·중동 시장 정조준',
            stocks=[
                StockItem('SNT모티브', '11.3%', '456억'),
                StockItem('센서뷰', '9.64%', '123억'),
                StockItem('파이버프로', '5.87%', '89억'),
                StockItem('한화에어로스페이스', '5.1%', '2,345억'),
                StockItem('우리기술', '4.97%', '67억'),
            ]
        ),
        CardData(
            card_type='theme',
            group_name='기타',
            main_issue='기타 이슈 종목 모음',
            stocks=[
                StockItem('A종목', '5.2%', '120억'),
                StockItem('B종목', '-3.1%', '80억'),
                StockItem('C종목', '-7.5%', '1,200억'),
            ]
        ),
        CardData(
            card_type='individual',
            group_name='개별이슈',
            stocks=[
                StockItem('코칩', '29.98%', '890억', '美 엔비디아에 블랙웰 "슈퍼커패시터" 공급... AI 서버 밸류체인 편입'),
                StockItem('뉴인텍', '29.85%', '1,567억', '"전기차株" 뉴인텍, 보조금 확대 소식에 ↑'),
            ]
        ),
    ]


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='장중 강세테마 동향 이미지 자동 생성')
    parser.add_argument('--date', type=str, help='조회할 날짜 (예: 2025.12.03)')
    parser.add_argument('--test', action='store_true', help='테스트 데이터로 실행')
    args = parser.parse_args()

    print("=" * 50)
    print("🚀 장중 강세테마 동향 자동화 시작")
    print("=" * 50)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if args.test:
        print("\n🧪 테스트 모드: 더미 데이터 사용")
        cards = create_test_data()
        target_date = "2025.12.03"
    else:
        print("\n📡 구글 시트 시트3에서 데이터 가져오는 중...")
        try:
            reader = SheetReaderTheme(CREDENTIALS_PATH, SPREADSHEET_ID)
            reader.connect()

            target_date = args.date if args.date else None
            raw_data = reader.get_today_data(target_date)

            if target_date is None:
                target_date = reader.get_latest_date()

            print(f"📅 대상 날짜: {target_date}")

            if not raw_data:
                print(f"⚠️ {target_date} 날짜의 데이터가 없습니다!")
                print("   테스트 모드로 전환합니다...")
                cards = create_test_data()
                target_date = "2025.12.03"
            else:
                cards = reader.group_data(raw_data)

        except Exception as e:
            print(f"❌ 구글 시트 연결 실패: {e}")
            print("   테스트 모드로 전환합니다...")
            cards = create_test_data()
            target_date = "2025.12.03"

    print(f"\n📦 총 {len(cards)}개의 카드 생성 예정")

    print("\n🎨 이미지 생성 중 (HTML → 스크린샷)...")
    renderer = HtmlRendererTheme(BASE_DIR)

    date_short = target_date.replace(".", "")
    output_path = os.path.join(OUTPUT_DIR, f"강세테마_{date_short}")

    output_files = renderer.generate(cards, target_date, output_path)

    print("\n" + "=" * 50)
    print("✅ 이미지 생성 완료!")
    print("=" * 50)
    for f in output_files:
        print(f"   📁 {f}")
    print("\n")

    return output_files


if __name__ == "__main__":
    main()
