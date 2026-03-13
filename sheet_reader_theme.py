"""
구글 시트 데이터 읽기 모듈 (장중 강세테마 동향용 - 시트3)
- 시트1 급등이슈와 동일 구조 + F열 거래대금, G열 이슈내용
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class StockItem:
    """개별 종목 데이터"""
    name: str           # 종목명
    change_rate: str    # 등락률
    volume: str = ""    # 거래대금
    issue: str = ""     # 이슈내용


@dataclass
class CardData:
    """카드 하나에 들어갈 데이터"""
    card_type: str              # 'theme' 또는 'individual'
    group_name: str             # 그룹명/섹터명
    main_issue: str = ""        # 테마형: 메인 이슈 설명
    stocks: List[StockItem] = field(default_factory=list)


class SheetReaderTheme:
    """구글 시트 시트3 데이터 리더 (장중 강세테마 동향)"""

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]

    def __init__(self, credentials_path: str, spreadsheet_id: str):
        self.credentials_path = credentials_path
        self.spreadsheet_id = spreadsheet_id
        self.client = None
        self.sheet = None

    def connect(self):
        """구글 시트에 연결"""
        credentials = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=self.SCOPES
        )
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open_by_key(self.spreadsheet_id)
        print(f"✅ 구글 시트 연결 성공: {self.sheet.title}")

    def get_latest_date(self) -> str:
        """시트3에서 가장 최근 날짜를 찾아 반환"""
        worksheet = self.sheet.get_worksheet(2)  # 시트3 (0-indexed)
        all_records = worksheet.get_all_records()

        dates = set()
        for row in all_records:
            date_value = str(row.get('날짜', row.get('A', ''))).strip()
            if date_value:
                if len(date_value.split('.')) == 2:
                    date_value = f"2025.{date_value}"
                dates.add(date_value)

        if dates:
            latest = sorted(dates, reverse=True)[0]
            print(f"📅 시트3 최신 날짜: {latest}")
            return latest
        return datetime.now().strftime("%Y.%m.%d")

    def get_today_data(self, target_date: str = None) -> List[Dict[str, Any]]:
        """시트3에서 지정된 날짜의 데이터를 가져옴"""
        if target_date is None:
            target_date = self.get_latest_date()

        worksheet = self.sheet.get_worksheet(2)  # 시트3
        all_records = worksheet.get_all_records()

        today_data = []
        for row in all_records:
            date_value = str(row.get('날짜', row.get('A', ''))).strip()

            if self._match_date(date_value, target_date):
                today_data.append({
                    'date': date_value,
                    'type': str(row.get('타입', row.get('B', ''))).strip(),
                    'group': str(row.get('그룹명', row.get('C', ''))).strip(),
                    'stock': str(row.get('종목명', row.get('D', ''))).strip(),
                    'change': str(row.get('등락률', row.get('E', ''))).strip(),
                    'volume': str(row.get('거래대금', row.get('F', ''))).strip(),
                    'issue': str(row.get('이슈내용', row.get('G', ''))).strip()
                })

        print(f"📊 {target_date} 데이터: {len(today_data)}개 행")
        return today_data

    def _match_date(self, date_value: str, target_date: str) -> bool:
        """날짜 매칭 (다양한 형식 지원)"""
        if not date_value:
            return False
        if date_value == target_date:
            return True
        target_short = target_date.split('.')[-2] + '.' + target_date.split('.')[-1]
        if date_value == target_short:
            return True
        if date_value.replace('-', '.') == target_date:
            return True
        return False

    def group_data(self, raw_data: List[Dict]) -> List[CardData]:
        """
        원본 데이터를 카드 단위로 그룹화
        (급등이슈와 동일 로직 + 거래대금 포함)
        """
        MAX_STOCKS_PER_CARD = 5

        theme_groups: Dict[str, dict] = {}
        individual_items: List[StockItem] = []

        for row in raw_data:
            stock = StockItem(
                name=row['stock'],
                change_rate=self._format_change_rate(row['change']),
                volume=self._format_volume(row['volume']),
                issue=row['issue']
            )

            row_type = row['type'].strip()

            if row_type == '테마':
                group_name = row['group']
                if group_name not in theme_groups:
                    theme_groups[group_name] = {
                        'main_issue': row['issue'],
                        'stocks': []
                    }
                theme_groups[group_name]['stocks'].append(stock)

            elif row_type in ['개별', '개별이슈']:
                individual_items.append(stock)

        cards: List[CardData] = []

        # 테마 그룹을 등락률 합계 기준으로 정렬
        def get_group_rate_sum(group_data):
            total = 0.0
            for stock in group_data['stocks']:
                try:
                    rate_str = stock.change_rate.replace('+', '').replace('%', '').strip()
                    total += float(rate_str)
                except (ValueError, AttributeError):
                    pass
            return total

        sorted_theme_groups = sorted(
            theme_groups.items(),
            key=lambda x: get_group_rate_sum(x[1]),
            reverse=True
        )

        def parse_rate(stock):
            try:
                rate_str = stock.change_rate.replace('+', '').replace('%', '').strip()
                return float(rate_str)
            except (ValueError, AttributeError):
                return 0.0

        # 테마 카드들 추가
        for group_name, data in sorted_theme_groups:
            stocks = sorted(data['stocks'], key=parse_rate, reverse=True)
            main_issue = data['main_issue']

            if len(stocks) <= MAX_STOCKS_PER_CARD:
                cards.append(CardData(
                    card_type='theme',
                    group_name=group_name,
                    main_issue=main_issue,
                    stocks=stocks
                ))
                print(f"  📦 테마 카드: {group_name} ({len(stocks)}종목)")
            else:
                chunks = self._chunk_list(stocks, MAX_STOCKS_PER_CARD)
                for i, chunk in enumerate(chunks):
                    cards.append(CardData(
                        card_type='theme',
                        group_name=group_name,
                        main_issue=main_issue,
                        stocks=chunk
                    ))
                    print(f"  📦 테마 카드: {group_name} #{i+1} ({len(chunk)}종목)")

        # 개별이슈: 등락률 높은 순으로 정렬 후 3개씩 청킹
        if individual_items:
            individual_items_sorted = sorted(individual_items, key=parse_rate, reverse=True)
            chunks = self._chunk_list(individual_items_sorted, 3)
            for i, chunk in enumerate(chunks):
                cards.append(CardData(
                    card_type='individual',
                    group_name='개별이슈',
                    stocks=chunk
                ))
                print(f"  📦 개별이슈 카드 #{i+1}: {len(chunk)}종목")

        print(f"\n🎴 총 카드 수: {len(cards)}장")
        return cards

    def _format_change_rate(self, rate: str) -> str:
        """등락률 포맷 정리"""
        rate = rate.strip()
        if not rate:
            return "0%"
        if '%' not in rate:
            rate = rate + '%'
        rate = rate.replace('+', '')
        return rate

    def _format_volume(self, volume: str) -> str:
        """거래대금 포맷 정리"""
        volume = volume.strip()
        if not volume:
            return ""
        return volume

    def _chunk_list(self, lst: List, chunk_size: int) -> List[List]:
        """리스트를 chunk_size 단위로 분할"""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
