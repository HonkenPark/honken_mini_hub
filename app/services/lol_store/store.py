import asyncio
from playwright.async_api import async_playwright
from typing import List, Dict, Any
import json
from datetime import datetime
import pytz
import os
from pathlib import Path

class LoLStoreService:
    def __init__(self):
        self.data_file = Path("data/lol_store/discounts.json")
        self.exception_file = Path("data/lol_store/discounts.json")
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.last_update = None
        self.discounts = []
        self.exception_list = self._load_exception_list()
        self._load_data()

    def _load_exception_list(self) -> List[Dict[str, str]]:
        """Load exception list from JSON file"""
        if self.exception_file.exists():
            with open(self.exception_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("discounts", [])
        return []

    def _is_in_exception_list(self, result: Dict[str, Any]) -> bool:
        """Check if the result is in exception list"""
        for exception in self.exception_list:
            if (result["name"] == exception["name"] and 
                result["discount"] == exception["discount"]):
                return True
        return False

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

    async def scroll_and_collect_data(self, page, pause=100, max_scrolls=300, is_exception=False):
        skipped_count = 0
        all_results = []
        last_count = 0
        scroll_step = 8000
        
        for i in range(max_scrolls):
            current_results = await self.fetch_discounted_skins(page)
            
            for result in current_results:
                # Skip if result is in exception list
                if self._is_in_exception_list(result) and is_exception == False:
                    skipped_count += 1
                    print(f"Skipping exception item: {result['name']} ({result['discount']})")
                    continue
                    
                if result not in all_results:
                    all_results.append(result)
            
            # 현재 스크롤 위치와 페이지 높이 확인
            scroll_info = await page.evaluate("""
            () => {
                return {
                    scrollY: window.scrollY,
                    scrollHeight: document.documentElement.scrollHeight,
                    clientHeight: document.documentElement.clientHeight
                }
            }
            """)
            
            # 스크롤이 끝에 도달했는지 확인
            is_bottom = scroll_info['scrollY'] + scroll_info['clientHeight'] >= scroll_info['scrollHeight']
            
            # 스크롤이 끝에 도달했거나, 연속 3번 새로운 항목이 발견되지 않으면 종료
            if is_bottom:
                print(f"스크롤 종료: {'페이지 끝 도달' if is_bottom else '새로운 항목 없음'}")
                break
            
            await page.evaluate(f"""
            () => {{
                const currentScroll = window.scrollY;
                window.scrollTo(0, currentScroll + {scroll_step});
            }}
            """)
            await page.wait_for_timeout(pause)

            count = await page.evaluate("document.querySelectorAll('.sale-discount').length")
            print(f"[스크롤 {i+1}] 현재 할인 항목 개수: {count}, 수집된 고유 항목: {len(all_results)}")

            # if len(all_results) + skipped_count == 15:
            #     print("15개의 고유한 할인 항목을 모두 찾았습니다.")
            #     break
            last_count = count

        return all_results

    async def fetch_all_discounted_skins(self, is_exception):
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

            all_results = await self.scroll_and_collect_data(page, pause=150, is_exception=is_exception)
            await browser.close()

            if not all_results:
                print("⚠️ 아무 항목도 찾지 못했습니다.")
                return []
            else:
                print(f"✅ 총 {len(all_results)}개 항목을 찾았습니다.")
                return all_results
            
    async def update_exception_discounts(self):
        """Update exception discount information by scraping"""
        try:
            results = await self.fetch_all_discounted_skins(is_exception=True)
            self.discounts = results
            self.last_update = datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
            self._save_data()
            print(f"Scraping completed at {self.last_update}")
            return self.discounts
        except Exception as e:
            print(f"Error during scheduled scraping: {str(e)}")
            return []

    async def update_discounts(self):
        """Update discount information by scraping"""
        try:
            results = await self.fetch_all_discounted_skins(is_exception=False)
            self.discounts = results
            self.last_update = datetime.now(pytz.timezone('Asia/Seoul')).isoformat()
            self._save_data()
            print(f"Scraping completed at {self.last_update}")
            return self.discounts
        except Exception as e:
            print(f"Error during scheduled scraping: {str(e)}")
            return []

    async def get_discounts(self):
        """Get current discount information"""
        if not self.discounts:
            self._load_data()
        return {
            "last_update": self.last_update,
            "discounts": self.discounts
        }

    def _save_data(self):
        """Save data to JSON file"""
        data = {
            "last_update": self.last_update,
            "discounts": self.discounts
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_data(self):
        """Load data from JSON file"""
        if self.data_file.exists():
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.last_update = data.get("last_update")
                self.discounts = data.get("discounts", []) 