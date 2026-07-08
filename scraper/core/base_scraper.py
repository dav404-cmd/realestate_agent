from playwright.async_api import async_playwright
import asyncio
from pathlib import Path
import json
import pandas as pd
import os

from manage_db.db_manager_v1 import DbManagerV1
from manage_db.image_db_manager import ImageDb

# the base script for scrapers.

class BaseScraper:
    def __init__(self,table_name:str | None,source:str | None):
        self.root_path = Path(__file__).parents[2].resolve()
        self.playwright = None
        self.browser = None
        self.context = None
        self.main_page = None

        self.listing_db = DbManagerV1(table_name,source)
        self.image_db = ImageDb()

    async def start_browser(self):
        self.playwright = await async_playwright().start()
        # Keep headless False so Playwright loads a full browser profile,
        # but use chrome args to natively hide the visual window.
        launch_args = {
            "headless": False,
            "args": [
                "--headless=new",  # Natively hides the UI window
                "--disable-blink-features=AutomationControlled"  # Removes basic automation flags
            ]
        }
        self.browser = await self.playwright.chromium.launch(**launch_args)
        # Match your viewport and extra headers to look completely like a real desktop
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False,
            ignore_https_errors=True
        )
        self.main_page = await self.context.new_page()

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def store_csv(self,data,file_name,append_mode = True):
        data_dir = self.root_path / "data" / "raw"
        data_dir.mkdir(exist_ok=True)

        output_file = data_dir / f"{file_name}.csv"

        # Ensure data is a list of dicts
        if isinstance(data, dict):
            data = [data]

        df = pd.DataFrame(data)

        if append_mode:
            file_exists = output_file.exists()
            file_empty = not file_exists or os.path.getsize(output_file) == 0

            df.to_csv(
                output_file,
                mode='a',
                header=file_empty,
                index=False
            )
            print(f"Appended to CSV: {output_file}")
        else:
            df.to_csv(output_file, index=False)
            print(f"Overwriting to CSV: {output_file}")

    def store_json(self, data, file_name):
        data_dir = self.root_path / "data" / "raw"
        data_dir.mkdir(exist_ok=True)

        output_file = data_dir / f"{file_name}.json"

        if output_file.exists():
            try:
                text = output_file.read_text(encoding="utf-8-sig").strip()

                if text:
                    old = json.loads(text)
                else:
                    old = []

                if isinstance(old, list) and isinstance(data, list):
                    new = old + data
                else:
                    new = data

            except Exception as e:
                print(f"error in storing json : {e}")
                new = data
        else:
            new = data

        output_file.write_text(
            json.dumps(new, indent=2, ensure_ascii=False),
            encoding="utf-8-sig"
        )

    async def store_db_v1(self , dic_list):
        ids = await asyncio.to_thread(self.listing_db.insert_data,dic_list)
        print(f"Inserted {len(ids)} new rows , skipped {len(dic_list) - len(ids)} duplicates.")
        return ids

    async def store_image(self,listing_id,urls):
        ids = await asyncio.to_thread(self.image_db.insert_ima_url,listing_id,urls)
        print(f"Inserted {len(ids)} new rows into image db .")
        return ids
