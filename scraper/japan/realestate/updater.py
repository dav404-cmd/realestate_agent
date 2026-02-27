import asyncio

from scraper.japan.realestate.xpaths import EXPIRED
from scraper.core.base_scraper import BaseScraper
from manage_db.db_manager import DbManager

from utils.logger import get_logger

res_updater = get_logger("RealEstateUpdater")

db = DbManager(table_name="jp_realestate")

class UpdateRealEstate(BaseScraper):
    async def update_card(self,listing_ids,urls,start_browser = True):
        if start_browser:
            await self.start_browser()

        async def handle_update(listing_id,url,index):
            page = await self.context.new_page()

            try:

                await page.goto(url,timeout=15000,wait_until="domcontentloaded")
                res_updater.info(f"{index} Opened url : {url}")

                if listing_id is None:
                    res_updater.warning(f"{index} No db entry found for {url}")
                    return

                element = await page.query_selector(EXPIRED)
                if element:
                    res_updater.info(f"{index} Expired message detected : {url}")
                    db.update_status(listing_id,"expired")
                else:
                    db.update_status(listing_id, "active")

                db.update_last_update(listing_id)

            except Exception as e:
                res_updater.exception(f"Error during update:{e}")

            finally:
                await page.close()

        sem = asyncio.Semaphore(5)

        async def limit_task(i, listing_id, url):
            async with sem:
                await handle_update(listing_id=listing_id, url=url, index=i)

        await asyncio.gather(
            *(limit_task(i, listing_id, url) for i, (listing_id, url) in enumerate(zip(listing_ids, urls)))
        )

        if start_browser:
            db.close_conn()
            await self.close_browser()

    async def continuous_update(self, interval_sec=300):
        await self.start_browser()


        try:
            while True:
                res_updater.info("Starting update cycle")

                df = db.get_active_urls()

                listing_ids = df["id"].tolist()
                urls = df["url"].tolist()

                if not listing_ids or not urls:
                    res_updater.warning("No active listing found")
                    await asyncio.sleep(interval_sec)
                    continue

                await self.update_card(listing_ids,urls, start_browser=False)

                res_updater.info("Update cycle completed.")
                await asyncio.sleep(interval_sec)

        except KeyboardInterrupt:
            res_updater.exception("Cycle stopped by user")
        except Exception as e:
            res_updater.exception(f"Error {e}")

        finally:
            db.close_conn()
            await self.close_browser()


if __name__ == "__main__":
    updater = UpdateRealEstate()
    task = updater.continuous_update()
    asyncio.run(task)