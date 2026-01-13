"""
Airtable 데이터 읽기 모듈
- Airtable API를 통해 종목 데이터를 가져옴
- 답안지유형별로 그룹화하여 반환
"""

from pyairtable import Api
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class StockItem:
    """개별 종목 데이터"""
    종목명: str
    핵심키워드: str = ""
    편입일: str = ""
    답안지유형: List[str] = field(default_factory=list)  # Multiple select
    상태: str = ""
    국가: str = ""
    대분류: str = ""
    소분류: str = ""
    핵심일정: str = ""


@dataclass
class CategoryGroup:
    """대분류별 그룹 (시대흐름용)"""
    대분류: str
    종목들: List[StockItem] = field(default_factory=list)


@dataclass
class CountryGroup:
    """국가별 그룹 (시대흐름용)"""
    국가: str
    카테고리들: List[CategoryGroup] = field(default_factory=list)


class AirtableReader:
    """Airtable 데이터 리더"""
    
    def __init__(self, api_key: str, base_id: str, table_id: str):
        """
        Args:
            api_key: Airtable Personal Access Token
            base_id: Base ID (예: appA4t9o1QMTDZul7)
            table_id: Table ID (예: tbllRbqwpfEY8dV2O)
        """
        self.api_key = api_key
        self.base_id = base_id
        self.table_id = table_id
        self.api = None
        self.table = None
        
    def connect(self):
        """Airtable에 연결"""
        self.api = Api(self.api_key)
        self.table = self.api.table(self.base_id, self.table_id)
        print(f"✅ Airtable 연결 성공")
        
    def get_all_stocks(self) -> List[StockItem]:
        """
        모든 종목 데이터를 가져옴
        
        Returns:
            StockItem 리스트
        """
        records = self.table.all()
        stocks = []
        
        for record in records:
            fields = record.get('fields', {})
            
            # 답안지유형은 Multiple select이므로 리스트로 처리
            답안지유형 = fields.get('답안지유형', [])
            if isinstance(답안지유형, str):
                답안지유형 = [답안지유형]
            
            stock = StockItem(
                종목명=fields.get('종목명', ''),
                핵심키워드=fields.get('핵심키워드', ''),
                편입일=self._format_date(fields.get('편입일', '')),
                답안지유형=답안지유형,
                상태=fields.get('상태', ''),
                국가=fields.get('국가', ''),
                대분류=fields.get('대분류', ''),
                소분류=fields.get('소분류', ''),
                핵심일정=fields.get('핵심일정', '')
            )
            
            # 종목명이 있는 것만 추가
            if stock.종목명:
                stocks.append(stock)
        
        print(f"📊 총 {len(stocks)}개 종목 로드 완료")
        return stocks
    
    def _format_date(self, date_str: str) -> str:
        """날짜 포맷 정리 (YYYY-MM-DD → YY.MM.DD)"""
        if not date_str:
            return "-"
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return date.strftime("%y.%m.%d")
        except:
            return date_str
    
    def filter_by_type(self, stocks: List[StockItem], type_name: str) -> List[StockItem]:
        """
        답안지유형으로 필터링
        
        Args:
            stocks: 전체 종목 리스트
            type_name: 필터할 유형 (시대흐름, 슈퍼픽, 일정매매)
            
        Returns:
            해당 유형의 종목 리스트
        """
        return [s for s in stocks if type_name in s.답안지유형]
    
    def group_시대흐름_by_country_category(self, stocks: List[StockItem]) -> List[CountryGroup]:
        """
        시대흐름 종목을 국가별 → 대분류별로 그룹화
        
        Args:
            stocks: 시대흐름 종목 리스트
            
        Returns:
            CountryGroup 리스트 (국가별 → 대분류별 구조)
        """
        # 국가별 → 대분류별 그룹화
        country_dict: Dict[str, Dict[str, List[StockItem]]] = defaultdict(lambda: defaultdict(list))
        
        for stock in stocks:
            country = stock.국가 or '기타'
            category = stock.대분류 or '기타'
            country_dict[country][category].append(stock)
        
        # 데이터 구조 변환
        result = []
        
        # 국가 순서: 한국 먼저, 그 다음 미국, 나머지는 알파벳순
        country_order = ['한국', '미국']
        sorted_countries = sorted(
            country_dict.keys(),
            key=lambda x: (country_order.index(x) if x in country_order else 999, x)
        )
        
        for country in sorted_countries:
            categories = country_dict[country]
            category_groups = []
            
            # 대분류별로 정렬 (가나다순)
            for category in sorted(categories.keys()):
                stocks_in_category = categories[category]
                category_groups.append(CategoryGroup(
                    대분류=category,
                    종목들=stocks_in_category
                ))
            
            result.append(CountryGroup(
                국가=country,
                카테고리들=category_groups
            ))
        
        return result
    
    def get_grouped_data(self) -> Dict[str, Any]:
        """
        모든 데이터를 유형별로 그룹화하여 반환
        
        Returns:
            {
                '시대흐름': List[CountryGroup],
                '슈퍼픽': List[StockItem],
                '일정매매': List[StockItem]
            }
        """
        all_stocks = self.get_all_stocks()
        
        # 유형별 필터링
        시대흐름 = self.filter_by_type(all_stocks, '시대흐름')
        슈퍼픽 = self.filter_by_type(all_stocks, '슈퍼픽')
        일정매매 = self.filter_by_type(all_stocks, '일정매매')
        
        print(f"\n📦 유형별 종목 수:")
        print(f"  - 시대흐름: {len(시대흐름)}개")
        print(f"  - 슈퍼픽: {len(슈퍼픽)}개")
        print(f"  - 일정매매: {len(일정매매)}개")
        
        # 시대흐름은 국가별/대분류별로 추가 그룹화
        시대흐름_grouped = self.group_시대흐름_by_country_category(시대흐름)
        
        return {
            '시대흐름': 시대흐름_grouped,
            '슈퍼픽': 슈퍼픽,
            '일정매매': 일정매매
        }


# 테스트용
if __name__ == "__main__":
    # config_airtable.py에서 설정 로드
    try:
        from config_airtable import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID
    except ImportError:
        import os
        AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY", "")
        AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "")
        AIRTABLE_TABLE_ID = os.environ.get("AIRTABLE_TABLE_ID", "")
    
    reader = AirtableReader(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)
    reader.connect()
    
    data = reader.get_grouped_data()
    
    # 결과 출력
    print("\n=== 시대흐름 ===")
    for country_group in data['시대흐름']:
        print(f"\n🌍 {country_group.국가}")
        for category in country_group.카테고리들:
            print(f"  📁 {category.대분류}")
            for stock in category.종목들:
                print(f"    • {stock.종목명} ({stock.상태})")
    
    print("\n=== 슈퍼픽 ===")
    for stock in data['슈퍼픽']:
        print(f"  • {stock.종목명} ({stock.상태})")
    
    print("\n=== 일정매매 ===")
    for stock in data['일정매매']:
        print(f"  • {stock.종목명} - {stock.핵심일정} ({stock.상태})")

