from playwright.async_api import async_playwright
import asyncio
from pathlib import Path
import json
import pandas as pd
import os

from manage_db.db_manager import DbManager

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

    def store_csv(self,data,file_name,append_mode = True):
        data_dir = self.root_path / "data"
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
        data_dir = self.root_path / "data"
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

    @staticmethod
    def store_db(table_name:str,source:str,dic_lis,create_table = True):
        db = DbManager(table_name,source)
        if create_table:
            db.create_table()

        ids = db.insert_listing(dic_lis)
        print(f"Inserted {len(ids)} new rows into {table_name}, skipped {len(dic_lis) - len(ids)} duplicates")
        db.close_conn()
        return ids




