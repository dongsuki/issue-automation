"""
구글 시트 데이터 읽기 모듈 - 등락률 순위용
시트2에서 재료별 종목 데이터를 읽어옴
"""

import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
from collections import Counter


@dataclass
class RankingStock:
    """등락률 순위 종목 데이터"""
    date: str           # 날짜
    material: str       # 재료
    stock_name: str     # 종목명
    change_rate: float  # 등락률 (숫자)
    change_rate_str: str  # 등락률 (표시용)
    volume: str         # 거래대금
    content: str        # 내용


@dataclass
class MaterialGroup:
    """재료별 그룹"""
    material: str       # 재료명
    stocks: List[RankingStock]  # 종목 리스트
    color: str          # 배경색 (같은 재료가 2개 이상일 때)
    is_single: bool     # 단일 종목 여부 (회색 처리)


class SheetReaderRanking:
    """구글 시트 데이터 리더 - 등락률 순위용"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    # 재료별 색상 (파스텔톤)
    MATERIAL_COLORS = [
        '#FFF9C4',  # 노란색
        '#C8E6C9',  # 초록색
        '#B2EBF2',  # 하늘색
        '#F8BBD0',  # 분홍색
        '#E1BEE7',  # 보라색
        '#FFCCBC',  # 주황색
        '#D7CCC8',  # 갈색
        '#CFD8DC',  # 회색-파랑
        '#FFE0B2',  # 살구색
        '#C5CAE9',  # 남색
    ]
    
    SINGLE_COLOR = '#E0E0E0'  # 회색 (단일 종목용)
    
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
        
    def get_ranking_data(self) -> List[RankingStock]:
        """
        시트2에서 등락률 순위 데이터를 가져옴 (모든 데이터)
        A열의 날짜가 오늘이 아니면 내용 앞에 [년.월.일] 형식으로 추가
        
        Returns:
            등락률 순위 데이터 리스트
        """
        # 오늘 날짜
        today = datetime.now()
        today_year = today.year
        today_month = today.month
        today_day = today.day
        
        print(f"📅 오늘 날짜: {today_year}.{today_month}.{today_day}")
        
        # 시트2 데이터 가져오기
        worksheet = self.sheet.get_worksheet(1)  # 시트2
        all_records = worksheet.get_all_records()
        
        # 모든 데이터 가져오기
        ranking_data = []
        for row in all_records:
            # 등락률 숫자 추출
            change_rate_str = str(row.get('등락률(%)', row.get('D', ''))).strip()
            if not change_rate_str:
                continue
                
            change_rate_num = self._extract_number(change_rate_str)
            
            # A열에서 날짜 가져오기
            date_str = str(row.get('날짜', row.get('A', ''))).strip()
            
            # 내용 가져오기
            content = str(row.get('내용', row.get('F', ''))).strip()
            
            # 날짜가 오늘이 아니면 내용 앞에 [년.월.일] 추가
            content = self._add_date_prefix(date_str, content, today_year, today_month, today_day)
            
            stock = RankingStock(
                date=date_str,
                material=str(row.get('재료', row.get('B', ''))).strip(),
                stock_name=str(row.get('종목명', row.get('C', ''))).strip(),
                change_rate=change_rate_num,
                change_rate_str=self._format_change_rate(change_rate_str),
                volume=self._format_volume(str(row.get('거래대금(백만)', row.get('E', ''))).strip()),
                content=content
            )
            
            # 빈 데이터 제외
            if stock.stock_name and stock.material:
                ranking_data.append(stock)
                    
        print(f"📊 시트2 데이터: {len(ranking_data)}개 행")
        return ranking_data
    
    def _add_date_prefix(self, date_str: str, content: str, today_year: int, today_month: int, today_day: int) -> str:
        """
        A열의 날짜가 오늘이 아니면 내용 앞에 [년.월.일] 형식으로 추가
        
        Args:
            date_str: A열의 날짜 문자열 (예: "2025.12.4", "2025.12.04", "25.12.4")
            content: 내용
            today_year, today_month, today_day: 오늘 날짜
        
        Returns:
            처리된 내용
        """
        import re
        
        if not date_str or not content:
            return content
        
        # 날짜 파싱 (2025.12.4, 2025.12.04, 25.12.4 등 지원)
        # 패턴: 년도(2자리 또는 4자리).월.일
        match = re.match(r'^(20)?(\d{2})[.\-/](\d{1,2})[.\-/](\d{1,2})$', date_str.strip())
        
        if not match:
            return content
        
        # 날짜 추출
        year = int(match.group(2))  # 2자리 년도 (예: 25)
        month = int(match.group(3))
        day = int(match.group(4))
        
        # 4자리 년도로 변환 (25 -> 2025)
        full_year = 2000 + year if year < 100 else year
        
        # 오늘 날짜인지 확인
        is_today = (full_year == today_year and month == today_month and day == today_day)
        
        if is_today:
            # 오늘이면 그대로 반환
            return content
        else:
            # 오늘이 아니면 [년.월.일] 형식으로 앞에 추가
            date_prefix = f"[{year:02d}.{month:02d}.{day:02d}]"
            return f"{date_prefix} {content}"
    
    def group_by_material(self, stocks: List[RankingStock]) -> List[MaterialGroup]:
        """
        재료별로 그룹화하고 색상 할당
        
        핵심 로직:
        1. 재료별로 종목 그룹화
        2. 같은 재료가 2개 이상인 경우: 고유 색상
        3. 같은 재료가 1개인 경우: 회색
        4. 각 그룹 내에서 등락률 순서대로 정렬
        5. 2개 이상 재료 먼저, 1개 재료 나중에 출력
        
        Returns:
            MaterialGroup 리스트 (2개 이상 재료 먼저, 1개 재료 나중)
        """
        # 재료별로 그룹화
        material_dict: Dict[str, List[RankingStock]] = {}
        for stock in stocks:
            if stock.material not in material_dict:
                material_dict[stock.material] = []
            material_dict[stock.material].append(stock)
        
        # 각 재료별 종목을 등락률 순서대로 정렬
        for material, stock_list in material_dict.items():
            stock_list.sort(key=lambda x: x.change_rate, reverse=True)
        
        # 2개 이상인 재료에만 색상 할당
        color_index = 0
        material_colors = {}
        multi_stock_groups = []  # 2개 이상
        single_stock_groups = []  # 1개
        
        for material, stock_list in material_dict.items():
            count = len(stock_list)
            
            if count >= 2:
                # 2개 이상: 고유 색상
                color = self.MATERIAL_COLORS[color_index % len(self.MATERIAL_COLORS)]
                color_index += 1
                group = MaterialGroup(
                    material=material,
                    stocks=stock_list,
                    color=color,
                    is_single=False
                )
                multi_stock_groups.append(group)
            else:
                # 1개: 회색
                group = MaterialGroup(
                    material=material,
                    stocks=stock_list,
                    color=self.SINGLE_COLOR,
                    is_single=True
                )
                single_stock_groups.append(group)
        
        # 각 그룹을 종목 등락률 합계 기준으로 정렬
        multi_stock_groups.sort(key=lambda g: sum(s.change_rate for s in g.stocks), reverse=True)
        single_stock_groups.sort(key=lambda g: sum(s.change_rate for s in g.stocks), reverse=True)
        
        # 2개 이상 재료 먼저, 1개 재료 나중에
        groups = multi_stock_groups + single_stock_groups
        
        print(f"\n🎨 재료별 그룹: {len(groups)}개")
        print(f"  - 2개 이상 재료: {len(multi_stock_groups)}개 (색상)")
        print(f"  - 1개 재료: {len(single_stock_groups)}개 (회색)")
        for group in groups:
            color_name = "회색" if group.is_single else "색상"
            print(f"  • {group.material}: {len(group.stocks)}종목 ({color_name})")
        
        return groups
    
    def _extract_number(self, value: str) -> float:
        """문자열에서 숫자 추출"""
        import re
        # 숫자와 소수점만 추출
        match = re.search(r'[-+]?\d*\.?\d+', value.replace(',', ''))
        if match:
            return float(match.group())
        return 0.0
    
    def _format_change_rate(self, rate: str) -> str:
        """등락률 포맷 정리"""
        rate = rate.strip()
        if not rate:
            return "0.00"
            
        # 숫자만 추출
        num = self._extract_number(rate)
        return f"{num:.2f}"
    
    def _format_volume(self, volume: str) -> str:
        """거래대금 포맷 정리"""
        volume = volume.strip()
        if not volume:
            return "0"
            
        # 숫자만 추출
        num = self._extract_number(volume)
        
        # 천 단위 콤마 추가
        return f"{int(num):,}"


# 테스트용
if __name__ == "__main__":
    import os
    
    # 경로 설정
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "service_account.json.json")
    SPREADSHEET_ID = "1dX8Diej7AQixm7fBrnrdUybxW2Au9QzyATYRBKZN_jk"
    
    # 테스트 실행
    reader = SheetReaderRanking(CREDENTIALS_PATH, SPREADSHEET_ID)
    reader.connect()
    
    # 모든 데이터 가져오기
    stocks = reader.get_ranking_data()
    
    # 재료별 그룹화
    groups = reader.group_by_material(stocks)
    
    # 결과 출력
    for group in groups:
        color_type = "회색" if group.is_single else "색상"
        print(f"\n=== {group.material} ({color_type}: {group.color}) ===")
        for stock in group.stocks:
            print(f"  {stock.stock_name} {stock.change_rate_str}% - {stock.content[:30]}...")

