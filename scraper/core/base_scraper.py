from playwright.async_api import async_playwright
import asyncio
from pathlib import Path
import pandas as pd

# the base script for scrapers.

class BaseScraper:
    def __init__(self):
        self.root_path = Path(__file__).parents[2].resolve()
        self.playwright = None
        self.browser = None
        self.context = None
        self.main_page = None


    async def start_browser(self):
        self.playwright = await async_playwright().start()
        launch_args = {"headless" : True}
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

    async def store_csv(self,data,file_name,append_mode = False):
        data_dir = self.root_path / "data"
        data_dir.mkdir(exist_ok=True)

        output_file = data_dir / f"{file_name}.csv"

        # Ensure data is a list of dicts
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)

        if append_mode:
            file_exists = output_file.exists()
            df.to_csv(output_file, mode='a', header=not file_exists, index=False)
            print(f"Appended to CSV: {output_file}")

        else:
            df.to_csv(output_file, index=False)
            print(f"Overwriting to CSV: {output_file}")


