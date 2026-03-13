"""
HTML 기반 이미지 생성 모듈 (장중 강세테마 동향용)
- 급등이슈 렌더러와 동일 + 거래대금 표시
"""

import os
import json
import asyncio
from typing import List
from playwright.async_api import async_playwright

from sheet_reader_theme import CardData


class HtmlRendererTheme:
    """HTML 템플릿을 이미지로 렌더링 (강세테마용)"""

    def __init__(self, assets_dir: str):
        self.assets_dir = assets_dir
        self.template_path = os.path.join(assets_dir, "template_theme.html")

    async def generate_async(self, cards: List[CardData], date_str: str, output_path: str) -> List[str]:
        """비동기 이미지 생성"""
        cards_per_page = 4
        pages = [cards[i:i + cards_per_page] for i in range(0, len(cards), cards_per_page)]

        output_files = []

        async with async_playwright() as p:
            browser = await p.chromium.launch()

            for page_num, page_cards in enumerate(pages):
                page = await browser.new_page()
                await page.set_viewport_size({"width": 1320, "height": 2000})

                html_content = self._generate_html(page_cards, date_str)

                temp_html = os.path.join(self.assets_dir, f"temp_theme_{page_num}.html")
                with open(temp_html, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                await page.goto(f"file:///{temp_html.replace(os.sep, '/')}")
                await page.wait_for_timeout(2000)

                if len(pages) > 1:
                    file_path = f"{output_path}_{page_num + 1}.png"
                else:
                    file_path = f"{output_path}.png"

                element = await page.query_selector("#page")
                if element:
                    await element.screenshot(path=file_path)
                else:
                    await page.screenshot(path=file_path)

                output_files.append(file_path)
                print(f"💾 저장 완료: {file_path}")

                os.remove(temp_html)
                await page.close()

            await browser.close()

        return output_files

    def generate(self, cards: List[CardData], date_str: str, output_path: str) -> List[str]:
        """동기 래퍼"""
        return asyncio.run(self.generate_async(cards, date_str, output_path))

    def _generate_html(self, cards: List[CardData], date_str: str) -> str:
        """HTML 콘텐츠 생성"""
        cards_json = json.dumps([self._card_to_dict(c) for c in cards], ensure_ascii=False)

        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        html = template.replace('/*CARDS_DATA_PLACEHOLDER*/[]', cards_json)
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
                    'volume': s.volume,
                    'issue': s.issue
                }
                for s in card.stocks
            ]
        }
