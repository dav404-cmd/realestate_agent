from pathlib import Path
import asyncio

from playwright.async_api import async_playwright

class RealestateScraper:
    def __init__(self):
        self.root_path = Path(__file__).parents[2].resolve()
        self.playwright = None
        self.browser = None
        self.context = None


    async def start_browser(self):
        self.playwright = await async_playwright().start()
        launch_args = {"headless" : False}
        self.browser = await self.playwright.chromium.launch(**launch_args)
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            ignore_https_errors=True
        )

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def scraper(self):
        await self.start_browser()
        url = "https://realestate.co.jp/en/forsale?building_type=house"
        url2 = "https://realestate.co.jp/en/forsale/view/1290951"

        page1 = await self.context.new_page()
        page2 = await self.context.new_page()

        await asyncio.gather(
            page1.goto(url),
            page2.goto(url2)
        )
        image_path = self.root_path / "image"
        await asyncio.gather(
            page1.screenshot(path=image_path / "outside.png"),
            page2.screenshot(path=image_path / "inside.png")
        )

        await self.close_browser()

if __name__ == "__main__":
    scrape = RealestateScraper()
    task = scrape.scraper()
    asyncio.run(task)
