"""
HTML 기반 이미지 생성 모듈
- HTML/CSS로 레이아웃 구성
- Playwright로 스크린샷 캡처
"""

import os
import json
import asyncio
from typing import List
from playwright.async_api import async_playwright

from sheet_reader import CardData


class HtmlRenderer:
    """HTML 템플릿을 이미지로 렌더링"""
    
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self.template_path = os.path.join(assets_dir, "template.html")
        
    async def generate_async(self, cards: List[CardData], date_str: str, output_path: str) -> List[str]:
        """
        비동기 이미지 생성
        
        Args:
            cards: 카드 데이터 리스트
            date_str: 날짜 문자열
            output_path: 출력 파일 경로 (확장자 제외)
            
        Returns:
            생성된 이미지 파일 경로 리스트
        """
        # 페이지당 6개 카드
        cards_per_page = 6
        pages = [cards[i:i + cards_per_page] for i in range(0, len(cards), cards_per_page)]
        
        output_files = []
        
        async with async_playwright() as p:
            # 브라우저 실행
            browser = await p.chromium.launch()
            
            for page_num, page_cards in enumerate(pages):
                # 새 페이지 생성 (1280px 너비, 높이 여유있게)
                page = await browser.new_page()
                await page.set_viewport_size({"width": 1320, "height": 2000})
                
                # HTML 생성
                html_content = self._generate_html(page_cards, date_str)
                
                # 임시 HTML 파일 저장
                temp_html = os.path.join(self.assets_dir, f"temp_page_{page_num}.html")
                with open(temp_html, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # 페이지 로드 (Tailwind + 구글폰트 로딩 대기)
                await page.goto(f"file:///{temp_html.replace(os.sep, '/')}")
                await page.wait_for_timeout(2000)  # CDN 폰트 로딩 대기
                
                # 스크린샷 저장
                if len(pages) > 1:
                    file_path = f"{output_path}_{page_num + 1}.png"
                else:
                    file_path = f"{output_path}.png"
                
                # 페이지 요소만 캡처
                element = await page.query_selector("#page")
                if element:
                    await element.screenshot(path=file_path)
                else:
                    await page.screenshot(path=file_path)
                
                output_files.append(file_path)
                print(f"💾 저장 완료: {file_path}")
                
                # 임시 파일 삭제
                os.remove(temp_html)
                await page.close()
            
            await browser.close()
        
        return output_files
    
    def generate(self, cards: List[CardData], date_str: str, output_path: str) -> List[str]:
        """동기 래퍼"""
        return asyncio.run(self.generate_async(cards, date_str, output_path))
    
    def _generate_html(self, cards: List[CardData], date_str: str) -> str:
        """HTML 콘텐츠 생성"""
        # 카드 데이터를 JSON으로 변환
        cards_json = json.dumps([self._card_to_dict(c) for c in cards], ensure_ascii=False)
        
        # 템플릿 읽기
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 데이터 주입
        html = template.replace('/*CARDS_DATA_PLACEHOLDER*/[]', cards_json)
        
        # 날짜 교체
        html = html.replace('/*DATE_PLACEHOLDER*/', date_str)
        
        return html
    
    def _card_to_dict(self, card: CardData) -> dict:
        """CardData를 dict로 변환"""
        return {
            'card_type': card.card_type,
            'group_name': card.group_name,
            'main_issue': card.main_issue,
            'stocks': [
                {
                    'name': s.name,
                    'change_rate': s.change_rate,
                    'issue': s.issue
                }
                for s in card.stocks
            ]
        }


# 테스트
if __name__ == "__main__":
    from sheet_reader import CardData, StockItem
    
    test_cards = [
        CardData(
            card_type='theme',
            group_name='반도체',
            main_issue='"반도체주 방긋" 기술주 랠리에 뉴욕증시 하루만에 반등',
            stocks=[
                StockItem('쓰리에이로직스', '10.37%'),
                StockItem('아이에스티이', '10.34%'),
                StockItem('심텍홀딩스', '10.27%'),
            ]
        ),
        CardData(
            card_type='individual',
            group_name='개별이슈',
            stocks=[
                StockItem('코칩', '29.98%', '美 엔비디아에 블랙웰 공급'),
            ]
        ),
    ]
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    renderer = HtmlRenderer(BASE_DIR)
    
    output_path = os.path.join(BASE_DIR, "output", "html_test")
    renderer.generate(test_cards, "2025.12.03", output_path)

