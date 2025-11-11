from pathlib import Path
import asyncio
from asyncio import Semaphore
import re

from playwright.async_api import async_playwright

from scraper.japan.realestate.xpaths import CARDS,DETAILS_LINK,INFO_TABLE
from scraper.japan.realestate.data_extractor import extract_data

class RealestateScraper:
    def __init__(self):
        self.root_path = Path(__file__).parents[3].resolve()
        self.playwright = None
        self.browser = None
        self.context = None
        self.main_page = None


    async def start_browser(self):
        self.playwright = await async_playwright().start()
        launch_args = {"headless" : False}
        self.browser = await self.playwright.chromium.launch(**launch_args)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )
        self.main_page = await self.context.new_page()

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    @staticmethod
    async def make_url(ids : list) -> list:
        urls = []
        for id in ids:
            url = f"https://realestate.co.jp/en/forsale/view/{id}"
            urls.append(url)
        return urls


    async def get_cards_id(self,url):
        await self.main_page.goto(url)
        cards = await self.main_page.query_selector_all(CARDS)
        print(f"found {len(cards)} cards")
        ids = []
        for card in cards:
            link = await card.query_selector(DETAILS_LINK)
            if link:
                href = await link.get_attribute('href')
                match = re.search(r'/view/(\d+)',href)
                if match:
                    ids.append(match.group(1))
            else:
                print("link not found.")
        print("found ids")
        print(ids)
        return ids

    async def collect_data(self, urls):

        scraped_results = []

        async def handle_page(url, index):
            page = await self.context.new_page()

            async def page_closer():
                await page.close()

            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                print(f"[{index}] Opened: {url}")

                await page.wait_for_selector(INFO_TABLE, timeout=15000)
                data = await extract_data(page, page_closer)

                if data:
                    data["url"] = url
                    scraped_results.append(data)
                else:
                    print(f"[{index}] No data extracted: {url}")

            except Exception as e:
                print(f"[{index}] Error scraping {url}: {e}")
                await page_closer()

        # Limit concurrency (to avoid hitting the site too hard)
        sem = asyncio.Semaphore(5)

        async def limited_task(i, url):
            async with sem:
                await handle_page(url, i)

        await asyncio.gather(*(limited_task(i, url) for i, url in enumerate(urls)))

        print(f"* Done scraping {len(scraped_results)} pages.")
        return scraped_results

    async def scraper(self,building_type = "house"):
        await self.start_browser()
        try:

            url = f"https://realestate.co.jp/en/forsale?building_type={building_type}"

            ids = await self.get_cards_id(url)

            urls = await self.make_url(ids)

            await self.collect_data(urls)
        except Exception as e:
            print(f"[scraper] Error :{e}")
        except KeyboardInterrupt:
            print(f"scraper stopped by user.")
        finally:
            await self.close_browser()

if __name__ == "__main__":
    scrape = RealestateScraper()
    task = scrape.scraper()
    asyncio.run(task)
