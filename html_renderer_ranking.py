"""
HTML 기반 이미지 생성 모듈 - 등락률 순위용
- HTML/CSS로 테이블 레이아웃 구성
- Playwright로 스크린샷 캡처
"""

import os
import json
import asyncio
from typing import List
from playwright.async_api import async_playwright

from sheet_reader_ranking import MaterialGroup


class HtmlRendererRanking:
    """HTML 템플릿을 이미지로 렌더링 - 등락률 순위용"""
    
    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self.template_path = os.path.join(assets_dir, "template_ranking.html")
        
    async def generate_async(self, groups: List[MaterialGroup], output_path: str) -> List[str]:
        """
        비동기 이미지 생성
        
        Args:
            groups: 재료별 그룹 리스트
            output_path: 출력 파일 경로 (확장자 제외)
            
        Returns:
            생성된 이미지 파일 경로 리스트
        """
        # 페이지당 최대 20개 종목
        MAX_STOCKS_PER_PAGE = 20
        
        # 그룹을 페이지별로 분할 (종목 수 기준)
        pages = []
        current_page = []
        current_stock_count = 0
        
        for group in groups:
            group_stock_count = len(group.stocks)
            
            # 현재 페이지에 추가하면 20개를 초과하는 경우
            if current_stock_count + group_stock_count > MAX_STOCKS_PER_PAGE and current_page:
                pages.append(current_page)
                current_page = [group]
                current_stock_count = group_stock_count
            else:
                current_page.append(group)
                current_stock_count += group_stock_count
        
        # 마지막 페이지 추가
        if current_page:
            pages.append(current_page)
        
        output_files = []
        
        async with async_playwright() as p:
            # 브라우저 실행
            browser = await p.chromium.launch()
            
            for page_num, page_groups in enumerate(pages):
                page = await browser.new_page()
                
                # 뷰포트 설정
                await page.set_viewport_size({"width": 1680, "height": 3000})
                
                # HTML 생성
                html_content = self._generate_html(page_groups)
                
                # 임시 HTML 파일 저장
                temp_html = os.path.join(self.assets_dir, f"temp_ranking_{page_num}.html")
                with open(temp_html, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                # 페이지 로드 (폰트 로딩 대기)
                await page.goto(f"file:///{temp_html.replace(os.sep, '/')}")
                await page.wait_for_timeout(2000)
                
                # 출력 파일명
                if len(pages) > 1:
                    output_file = f"{output_path}_{page_num + 1}.png"
                else:
                    output_file = f"{output_path}.png"
                
                # 스크린샷 저장
                element = await page.query_selector("#capture-area")
                if element:
                    await element.screenshot(path=output_file)
                else:
                    await page.screenshot(path=output_file)
                
                output_files.append(output_file)
                print(f"💾 저장 완료: {output_file}")
                
                # 임시 파일 삭제
                os.remove(temp_html)
                await page.close()
            
            await browser.close()
        
        return output_files
    
    def generate(self, groups: List[MaterialGroup], output_path: str) -> List[str]:
        """동기 래퍼"""
        return asyncio.run(self.generate_async(groups, output_path))
    
    def _generate_html(self, groups: List[MaterialGroup]) -> str:
        """HTML 콘텐츠 생성"""
        # 그룹 데이터를 JSON으로 변환
        groups_json = json.dumps([self._group_to_dict(g) for g in groups], ensure_ascii=False)
        
        # 템플릿 읽기
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # 데이터 주입
        html = template.replace('/*GROUPS_DATA_PLACEHOLDER*/[]', groups_json)
        
        return html
    
    def _group_to_dict(self, group: MaterialGroup) -> dict:
        """MaterialGroup을 dict로 변환"""
        return {
            'material': group.material,
            'color': group.color,
            'is_single': group.is_single,
            'stocks': [
                {
                    'stock_name': s.stock_name,
                    'change_rate_str': s.change_rate_str,
                    'volume': s.volume,
                    'content': s.content
                }
                for s in group.stocks
            ]
        }


# 테스트
if __name__ == "__main__":
    from sheet_reader_ranking import SheetReaderRanking, MaterialGroup, RankingStock
    
    # 테스트 데이터
    test_groups = [
        MaterialGroup(
            material='건설',
            stocks=[
                RankingStock('', '건설', '한신공영', 30.00, '30.00', '38,679', '정부 공급 확대 속도 소식에 건설 정상화 기대감에 상승'),
                RankingStock('', '건설', '동신건설', 29.31, '29.31', '12,704', '건설산업 정상화 정책 기대감에 건설株 상승'),
            ],
            color='#FFF9C4',
            is_single=False
        ),
        MaterialGroup(
            material='로봇',
            stocks=[
                RankingStock('', '로봇', '링크솔루션', 29.92, '29.92', '77,999', '2025.12.2 링크솔루션 "보스턴다이내믹스 로봇 샘플 25종" 테스트 통과 기대감'),
            ],
            color='#E0E0E0',
            is_single=True
        ),
    ]
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    renderer = HtmlRendererRanking(BASE_DIR)
    
    output_path = os.path.join(BASE_DIR, "output", "ranking_test")
    renderer.generate(test_groups, output_path)

