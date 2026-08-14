import asyncio

from scraper.japan.realestate.xpaths import EXPIRED
from scraper.core.base_scraper import BaseScraper
from scraper.japan.realestate.data_extractor import extract_images_via_overlay,extract_static_dom_data

from manage_db.db_manager_v1 import DbManagerV1
from manage_db.image_db_manager import ImageDb

from utils.logger import get_logger

res_updater = get_logger("RealEstateDataUpdater","scraper")

class MetaDataUpdater(BaseScraper):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.db = DbManagerV1(table_name="jp_realestate_v1")
        self.db_img = ImageDb()

    async def update_card(self,listing_ids,urls,image_ids,start_browser = True): #todo : fix the image extraction .
        if start_browser:
            await self.start_browser()

        async def handle_update(listing_id,url,index):
            page = await self.context.new_page()

            try:
                await page.goto(
                    url,
                    timeout=15000,
                    wait_until="domcontentloaded"
                )

                await page.wait_for_load_state("networkidle")

                res_updater.info(f"{index} Opened url : {url}")

                if listing_id is None:
                    res_updater.warning(f"{index} No db entry found for {url}")
                    return

                element = await page.query_selector(EXPIRED)
                if element:
                    res_updater.info(f"{index} Expired message detected : {url}")
                    self.db.update_status(listing_id,"expired")
                    self.db.update_last_update(listing_id)
                    return
                else:
                    self.db.update_status(listing_id, "active")
                    res_updater.info(f"{index} is live")

                    new_data = await extract_static_dom_data(page)

                    self.db.update_listing(listing_id,new_data)

                    if listing_id not in image_ids:
                        try:
                            await page.wait_for_selector("figure.cursor-pointer", timeout=5000)
                        except:
                            res_updater.info(f"{listing_id} has no gallery")

                        images = await extract_images_via_overlay(page) #todo: update data in update_status
                        self.db_img.insert_ima_url(listing_id,images)
                        res_updater.info(f"found image for {index}")

                self.db.update_last_update(listing_id)

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

                df = self.db.get_active_ids_metadata()
                image_ids = self.db_img.get_listing_ids_with_images()

                #make urls
                df["source_listing_id"] = df["source_listing_id"].apply(lambda ids : f"https://realestate.co.jp/en/forsale/view/{ids}")

                listing_ids = df["id"].tolist()
                urls = df["source_listing_id"].tolist()

                if not listing_ids or not urls:
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
                        image_ids=image_ids,
                        start_browser=False
                    )

                    self.db.conn.commit()

                    batch_number = start // BATCH_SIZE + 1

                    res_updater.info(
                        f"Finished batch {batch_number} "
                        f"({start}-{end - 1})"
                    )

                    if batch_wise and batch_number >= max_batches:
                        if batch_wise and batch_number >= max_batches:
                            res_updater.info(f"Stopped the updater after {batch_number}")
                            break


                res_updater.info("Update cycle completed.")
                await asyncio.sleep(interval_sec)

        except KeyboardInterrupt:
            res_updater.exception("Cycle stopped by user")
        except Exception as e:
            res_updater.exception(f"Error {e}")

        finally:
            self.db.close_conn()
            await self.close_browser()

if __name__ == "__main__":
    updater = MetaDataUpdater(None,None)
    task = updater.continuous_update()
    asyncio.run(task)