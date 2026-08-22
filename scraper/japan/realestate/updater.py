import asyncio

from scraper.japan.realestate.xpaths import EXPIRED
from scraper.core.base_scraper import BaseScraper

from manage_db.db_manager_v1 import DbManagerV1

from utils.logger import get_logger

res_updater = get_logger("RealEstateUpdater","scraper")

class UpdateRealEstate(BaseScraper):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.db = DbManagerV1(table_name="jp_realestate_v1")
        
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
                    self.db.update_status(listing_id,"expired")
                else:
                    self.db.update_status(listing_id, "active")
                    res_updater.info(f"{index} is live")

                self.db.update_last_update(listing_id) #todo: update data in update_status

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
            self.db.close_conn()
            await self.close_browser()

    async def continuous_update(self, interval_sec=300,batch_wise = True , max_batches = 1):
        await self.start_browser()

        BATCH_SIZE = 100
        try:
            while True:
                res_updater.info("Starting update cycle")

                df = self.db.get_active_ids()

                #make urls
                df["source_listing_id"] = df["source_listing_id"].apply(lambda ids : f"https://realestate.co.jp/en/forsale/view/{ids}")

                listing_ids = df["id"].tolist()
                urls = df["source_listing_id"].tolist()

                if not listing_ids or not urls: #todo:maybe close the updater
                    res_updater.warning("No active listing found")
                    if batch_wise:
                        break
                    await asyncio.sleep(interval_sec)
                    continue

                for start in range(0, len(listing_ids), BATCH_SIZE):
                    end = min(start + BATCH_SIZE, len(listing_ids))

                    await self.update_card(
                        listing_ids=listing_ids[start:end],
                        urls=urls[start:end],
                        start_browser=False
                    )

                    self.db.conn.commit()

                    batch_number = start // BATCH_SIZE + 1

                    res_updater.info(
                        f"Finished batch {batch_number} "
                        f"({start}-{end - 1})"
                    )
                    if batch_wise and batch_number >= max_batches:
                        res_updater.info(f"Stopped the updater after {batch_number}")
                        return


                await asyncio.sleep(interval_sec)

        except KeyboardInterrupt:
            res_updater.exception("Cycle stopped by user")
        except Exception as e:
            res_updater.exception(f"Error {e}")

        finally:
            self.db.close_conn()
            await self.close_browser()


if __name__ == "__main__":
    updater = UpdateRealEstate(None,None)
    task = updater.continuous_update()
    asyncio.run(task)