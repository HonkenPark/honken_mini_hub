import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict, Any
import json
from datetime import datetime
import pytz
import os

class LoLStoreService:
    def __init__(self):
        self.latest_results: List[Dict[str, Any]] = []
        self.last_scrape_time: datetime = None
        self.data_file = "data/scraping_results.json"

    async def fetch_discounted_skins(self, page):
        return await page.evaluate("""
        () => {
            let discounts = document.querySelectorAll('.sale-discount');
            let result = [];
            for (let i = 0; i < discounts.length; i++) {
                try {
                    const element = discounts[i].parentNode.parentElement.parentElement.children[0].children[0].children[0];
                    const imgUrl = element.dataset.assetUrl;
                    
                    let name = discounts[i].parentNode.parentElement.previousElementSibling.children[0].innerText;
                    let price = discounts[i].parentNode.parentElement.previousElementSibling.children[1]
                                .querySelectorAll('.price')[1].innerText;
                    let discount = discounts[i].innerText;
                    result.push({
                        url: imgUrl,
                        name: name,
                        price: price + ' RP',
                        discount: '-' + discount + '%'
                    });
                } catch (e) {
                    // 오류 무시
                }
            }
            return result;
        }
        """)

    async def scroll_and_collect_data(self, page, pause=100, max_scrolls=300):
        all_results = []
        last_count = 0
        scroll_step = 8000
        
        for i in range(max_scrolls):
            current_results = await self.fetch_discounted_skins(page)
            
            for result in current_results:
                if result not in all_results:
                    all_results.append(result)
            
            await page.evaluate(f"""
            () => {{
                const currentScroll = window.scrollY;
                window.scrollTo(0, currentScroll + {scroll_step});
            }}
            """)
            await page.wait_for_timeout(pause)

            count = await page.evaluate("document.querySelectorAll('.sale-discount').length")
            print(f"[스크롤 {i+1}] 현재 할인 항목 개수: {count}, 수집된 고유 항목: {len(all_results)}")

            if len(all_results) == 15:
                print("15개의 고유한 할인 항목을 모두 찾았습니다.")
                break
            last_count = count

        return all_results

    async def fetch_all_discounted_skins(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://store.leagueoflegends.co.kr/skins?sort=ReleaseDate&order=DESC")
            await page.wait_for_timeout(300)

            await page.evaluate("""
            () => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const saleFilter = buttons.find(btn => btn.innerText.includes('할인 중'));
                if (saleFilter) saleFilter.click();
            }
            """)
            await page.wait_for_timeout(300)

            all_results = await self.scroll_and_collect_data(page, pause=150)
            await browser.close()

            if not all_results:
                print("⚠️ 아무 항목도 찾지 못했습니다.")
                return []
            else:
                print(f"✅ 총 {len(all_results)}개 항목을 찾았습니다.")
                return all_results

    async def update_discounts(self):
        """스크래핑을 실행하고 결과를 저장합니다."""
        try:
            results = await self.fetch_all_discounted_skins()
            self.latest_results = results
            self.last_scrape_time = datetime.now(pytz.timezone('Asia/Seoul'))
            
            # 결과를 JSON 파일로 저장
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': self.last_scrape_time.isoformat(),
                    'results': self.latest_results
                }, f, ensure_ascii=False, indent=2)
                
            print(f"Scraping completed at {self.last_scrape_time}")
            return True
        except Exception as e:
            print(f"Error during scheduled scraping: {str(e)}")
            return False

    def get_latest_results(self):
        """최신 스크래핑 결과를 반환합니다."""
        return {
            "last_update": self.last_scrape_time,
            "count": len(self.latest_results),
            "results": self.latest_results
        }

    def get_last_update(self):
        """마지막 스크래핑 시간을 반환합니다."""
        return {"last_update": self.last_scrape_time} 