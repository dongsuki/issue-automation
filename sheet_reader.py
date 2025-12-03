"""
구글 시트 데이터 읽기 모듈
- 서비스 계정을 통해 구글 시트에 접속
- 오늘 날짜 데이터를 그룹별로 정리하여 반환
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
    issue: str = ""     # 이슈내용 (개별이슈용)


@dataclass  
class CardData:
    """카드 하나에 들어갈 데이터"""
    card_type: str              # 'theme' 또는 'individual'
    group_name: str             # 그룹명/섹터명
    main_issue: str = ""        # 테마형: 메인 이슈 설명
    stocks: List[StockItem] = field(default_factory=list)  # 종목 리스트


class SheetReader:
    """구글 시트 데이터 리더"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    def __init__(self, credentials_path: str, spreadsheet_id: str):
        """
        Args:
            credentials_path: 서비스 계정 JSON 파일 경로
            spreadsheet_id: 구글 시트 ID
        """
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
        """시트에서 가장 최근 날짜를 찾아 반환"""
        worksheet = self.sheet.sheet1
        all_records = worksheet.get_all_records()
        
        dates = set()
        for row in all_records:
            date_value = str(row.get('날짜', row.get('A', ''))).strip()
            if date_value:
                # 날짜 형식 통일 (12.04 → 2025.12.04)
                if len(date_value.split('.')) == 2:
                    date_value = f"2025.{date_value}"
                dates.add(date_value)
        
        if dates:
            # 가장 최근 날짜 반환
            latest = sorted(dates, reverse=True)[0]
            print(f"📅 시트 최신 날짜: {latest}")
            return latest
        return datetime.now().strftime("%Y.%m.%d")
    
    def get_today_data(self, target_date: str = None) -> List[Dict[str, Any]]:
        """
        지정된 날짜의 데이터를 가져옴
        
        Args:
            target_date: 조회할 날짜 (예: "2025.12.03"). None이면 시트의 최신 날짜
            
        Returns:
            해당 날짜의 모든 행 데이터 리스트
        """
        if target_date is None:
            target_date = self.get_latest_date()
            
        # 첫 번째 시트의 모든 데이터 가져오기
        worksheet = self.sheet.sheet1
        all_records = worksheet.get_all_records()
        
        # 해당 날짜 데이터만 필터링
        today_data = []
        for row in all_records:
            # A열(날짜) 확인 - 헤더명에 따라 조정 필요
            date_value = str(row.get('날짜', row.get('A', ''))).strip()
            
            # 날짜 형식 유연하게 매칭 (2025.12.03, 2025-12-03, 12.03 등)
            if self._match_date(date_value, target_date):
                today_data.append({
                    'date': date_value,
                    'type': str(row.get('타입', row.get('B', ''))).strip(),
                    'group': str(row.get('그룹명', row.get('C', ''))).strip(),
                    'stock': str(row.get('종목명', row.get('D', ''))).strip(),
                    'change': str(row.get('등락률', row.get('E', ''))).strip(),
                    'issue': str(row.get('이슈내용', row.get('F', ''))).strip()
                })
                
        print(f"📊 {target_date} 데이터: {len(today_data)}개 행")
        return today_data
    
    def _match_date(self, date_value: str, target_date: str) -> bool:
        """날짜 매칭 (다양한 형식 지원)"""
        # 빈 값 체크
        if not date_value:
            return False
            
        # 정확히 일치
        if date_value == target_date:
            return True
            
        # 연도 없이 비교 (12.03 == 2025.12.03)
        target_short = target_date.split('.')[-2] + '.' + target_date.split('.')[-1]
        if date_value == target_short:
            return True
            
        # 하이픈 형식 (2025-12-03)
        if date_value.replace('-', '.') == target_date:
            return True
            
        return False
    
    def group_data(self, raw_data: List[Dict]) -> List[CardData]:
        """
        원본 데이터를 카드 단위로 그룹화
        
        핵심 로직:
        1. 테마형: 같은 그룹명끼리 묶되, 5개 초과 시 분리
        2. 개별이슈형: 2개씩 청킹하여 여러 카드로 분리
        
        Returns:
            CardData 리스트 (각 카드별 데이터)
        """
        MAX_STOCKS_PER_CARD = 5  # 카드당 최대 종목 수
        
        theme_groups: Dict[str, dict] = {}  # 테마별 그룹 (이슈 + 종목리스트)
        individual_items: List[StockItem] = []  # 개별이슈 종목들
        
        for row in raw_data:
            stock = StockItem(
                name=row['stock'],
                change_rate=self._format_change_rate(row['change']),
                issue=row['issue']
            )
            
            row_type = row['type'].strip()
            
            if row_type == '테마':
                group_name = row['group']
                if group_name not in theme_groups:
                    theme_groups[group_name] = {
                        'main_issue': row['issue'],  # 첫 번째 행의 이슈를 메인으로
                        'stocks': []
                    }
                theme_groups[group_name]['stocks'].append(stock)
                
            elif row_type in ['개별', '개별이슈']:
                individual_items.append(stock)
        
        # 결과 리스트 생성
        cards: List[CardData] = []
        
        # 테마 카드들 추가 (5개 초과 시 분리)
        for group_name, data in theme_groups.items():
            stocks = data['stocks']
            main_issue = data['main_issue']
            
            if len(stocks) <= MAX_STOCKS_PER_CARD:
                # 5개 이하: 카드 1개
                cards.append(CardData(
                    card_type='theme',
                    group_name=group_name,
                    main_issue=main_issue,
                    stocks=stocks
                ))
                print(f"  📦 테마 카드: {group_name} ({len(stocks)}종목)")
            else:
                # 5개 초과: 분리 (이슈 설명은 동일하게 유지)
                chunks = self._chunk_list(stocks, MAX_STOCKS_PER_CARD)
                for i, chunk in enumerate(chunks):
                    cards.append(CardData(
                        card_type='theme',
                        group_name=group_name,
                        main_issue=main_issue,  # 동일한 이슈 설명 유지
                        stocks=chunk
                    ))
                    print(f"  📦 테마 카드: {group_name} #{i+1} ({len(chunk)}종목)")
            
        # 개별이슈: 3개씩 청킹
        if individual_items:
            chunks = self._chunk_list(individual_items, 3)
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
            
        # % 기호 없으면 추가
        if '%' not in rate:
            rate = rate + '%'
            
        # + 기호 제거 (양수는 그냥 숫자로)
        rate = rate.replace('+', '')
        
        return rate
    
    def _chunk_list(self, lst: List, chunk_size: int) -> List[List]:
        """리스트를 chunk_size 단위로 분할"""
        return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


# 테스트용
if __name__ == "__main__":
    import os
    
    # 경로 설정
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "service_account.json.json")
    SPREADSHEET_ID = "1dX8Diej7AQixm7fBrnrdUybxW2Au9QzyATYRBKZN_jk"
    
    # 테스트 실행
    reader = SheetReader(CREDENTIALS_PATH, SPREADSHEET_ID)
    reader.connect()
    
    # 오늘 데이터 가져오기 (또는 특정 날짜)
    raw_data = reader.get_today_data("2025.12.03")
    
    # 카드 단위로 그룹화
    cards = reader.group_data(raw_data)
    
    # 결과 출력
    for card in cards:
        print(f"\n--- {card.group_name} ({card.card_type}) ---")
        if card.main_issue:
            print(f"  이슈: {card.main_issue[:30]}...")
        for stock in card.stocks:
            print(f"  • {stock.name} ({stock.change_rate})")

