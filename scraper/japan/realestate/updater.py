import asyncio

from scraper.japan.realestate.xpaths import EXPIRED
from scraper.core.base_scraper import BaseScraper
from manage_db.db_manager import DbManager

db = DbManager(table_name="jp_realestate")

class UpdateRealEstate(BaseScraper):
    async def update_card(self,urls):
        await self.start_browser()

        async def handle_update(url,index):
            page = await self.context.new_page()

            try:

                await page.goto(url,timeout=3000,wait_until="domcontentloaded")
                print(f"{index} Opened url : {url}")

                listing_id = db.get_id_by_url(url)
                if listing_id is None:
                    print(f"{index} No db entry found for {url}")
                    return

                element = await page.query_selector(EXPIRED)
                if element:
                    print(f"{index} Expired message detected : {url}")
                    db.update_status(listing_id,"expired")
                else:
                    db.update_status(listing_id, "active")

            except Exception as e:
                print(f"Error during update:{e}")

            finally:
                await page.close()

        sem = asyncio.Semaphore(5)

        async def limit_task(i , url):
            async with sem:
                await handle_update(url,i)

        await asyncio.gather(*(limit_task(i,url) for i,url in enumerate(urls)))

        db.close_conn()
        await self.close_browser()

if __name__ == "__main__":
    urls = ["https://realestate.co.jp/en/forsale/view/1288204","https://realestate.co.jp/en/forsale/view/1256872","https://realestate.co.jp/en/forsale/view/1292935"]
    updater = UpdateRealEstate()
    task = updater.update_card(urls)
    asyncio.run(task)