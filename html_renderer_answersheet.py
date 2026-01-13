"""
HTML 기반 이미지 생성 모듈 - 답안지용
- HTML/CSS로 레이아웃 구성
- Playwright로 스크린샷 캡처
"""

import os
import json
import asyncio
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from dataclasses import asdict

from airtable_reader import StockItem, CategoryGroup, CountryGroup


class HtmlRendererAnswerSheet:
    """HTML 템플릿을 이미지로 렌더링 - 답안지용"""
    
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self.template_path = os.path.join(assets_dir, "template_answersheet.html")
        
    async def generate_async(self, data: Dict[str, Any], date_str: str, output_path: str) -> List[str]:
        """
        비동기 이미지 생성
        
        Args:
            data: 답안지 데이터 (시대흐름, 슈퍼픽, 일정매매)
            date_str: 날짜 문자열
            output_path: 출력 파일 경로 (확장자 제외)
            
        Returns:
            생성된 이미지 파일 경로 리스트
        """
        output_files = []
        
        async with async_playwright() as p:
            # 브라우저 실행
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # 뷰포트 설정 (600px 모바일 최적화)
            await page.set_viewport_size({"width": 650, "height": 8000})
            
            # HTML 생성
            html_content = self._generate_html(data, date_str)
            
            # 임시 HTML 파일 저장
            temp_html = os.path.join(self.assets_dir, "temp_answersheet.html")
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 페이지 로드 (폰트 로딩 대기)
            await page.goto(f"file:///{temp_html.replace(os.sep, '/')}")
            await page.wait_for_timeout(2500)  # CDN 폰트 로딩 대기
            
            # 출력 파일명
            output_file = f"{output_path}.png"
            
            # 캡처 영역만 스크린샷
            element = await page.query_selector("#capture-area")
            if element:
                await element.screenshot(path=output_file)
            else:
                await page.screenshot(path=output_file, full_page=True)
            
            output_files.append(output_file)
            print(f"💾 저장 완료: {output_file}")
            
            # 임시 파일 삭제
            os.remove(temp_html)
            await page.close()
            await browser.close()
        
        return output_files
    
    def generate(self, data: Dict[str, Any], date_str: str, output_path: str) -> List[str]:
        """동기 래퍼"""
        return asyncio.run(self.generate_async(data, date_str, output_path))
    
    def _generate_html(self, data: Dict[str, Any], date_str: str) -> str:
        """HTML 콘텐츠 생성"""
        # 데이터를 JSON으로 변환
        json_data = self._convert_to_json(data)
        
        # 템플릿 읽기
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 데이터 주입
        html = template.replace('/*DATA_PLACEHOLDER*/{}', json_data)
        
        # 날짜 교체
        html = html.replace('/*DATE_PLACEHOLDER*/', date_str)
        
        return html
    
    def _convert_to_json(self, data: Dict[str, Any]) -> str:
        """데이터를 JSON 문자열로 변환"""
        result = {}
        
        # 시대흐름 변환 (CountryGroup 리스트)
        if '시대흐름' in data:
            시대흐름_list = []
            for country_group in data['시대흐름']:
                country_dict = {
                    '국가': country_group.국가,
                    '카테고리들': []
                }
                for category in country_group.카테고리들:
                    category_dict = {
                        '대분류': category.대분류,
                        '종목들': [self._stock_to_dict(s) for s in category.종목들]
                    }
                    country_dict['카테고리들'].append(category_dict)
                시대흐름_list.append(country_dict)
            result['시대흐름'] = 시대흐름_list
        
        # 슈퍼픽 변환 (StockItem 리스트)
        if '슈퍼픽' in data:
            result['슈퍼픽'] = [self._stock_to_dict(s) for s in data['슈퍼픽']]
        
        # 일정매매 변환 (StockItem 리스트)
        if '일정매매' in data:
            result['일정매매'] = [self._stock_to_dict(s) for s in data['일정매매']]
        
        return json.dumps(result, ensure_ascii=False)
    
    def _stock_to_dict(self, stock: StockItem) -> dict:
        """StockItem을 dict로 변환"""
        return {
            '종목명': stock.종목명,
            '핵심키워드': stock.핵심키워드,
            '편입일': stock.편입일,
            '상태': stock.상태,
            '국가': stock.국가,
            '대분류': stock.대분류,
            '소분류': stock.소분류,
            '핵심일정': stock.핵심일정
        }


# 테스트
if __name__ == "__main__":
    from airtable_reader import AirtableReader, StockItem, CategoryGroup, CountryGroup
    
    # 테스트 데이터 생성
    test_data = {
        '시대흐름': [
            CountryGroup(
                국가='한국',
                카테고리들=[
                    CategoryGroup(
                        대분류='반도체',
                        종목들=[
                            StockItem(종목명='삼성전자', 소분류='메모리', 편입일='24.12.01', 상태='관심'),
                            StockItem(종목명='SK하이닉스', 소분류='메모리', 편입일='24.11.15', 상태='보유자관점'),
                        ]
                    ),
                    CategoryGroup(
                        대분류='2차전지',
                        종목들=[
                            StockItem(종목명='LG에너지솔루션', 소분류='배터리', 편입일='24.10.20', 상태='신규매수주의'),
                        ]
                    )
                ]
            ),
            CountryGroup(
                국가='미국',
                카테고리들=[
                    CategoryGroup(
                        대분류='AI',
                        종목들=[
                            StockItem(종목명='NVIDIA', 소분류='GPU', 편입일='24.09.01', 상태='관심'),
                        ]
                    )
                ]
            )
        ],
        '슈퍼픽': [
            StockItem(종목명='테스트종목A', 편입일='24.12.05', 상태='관심'),
            StockItem(종목명='테스트종목B', 편입일='24.11.20', 상태='분할매도'),
        ],
        '일정매매': [
            StockItem(종목명='일정종목A', 핵심일정='1월 15일 실적발표', 편입일='24.12.10', 상태='관심'),
            StockItem(종목명='일정종목B', 핵심일정='2월 CES 참가', 편입일='24.12.08', 상태='보유자관점'),
        ]
    }
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    renderer = HtmlRendererAnswerSheet(BASE_DIR)
    
    output_path = os.path.join(BASE_DIR, "output", "answersheet_test")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    renderer.generate(test_data, "2025.01.13", output_path)
    print("✅ 테스트 이미지 생성 완료!")

