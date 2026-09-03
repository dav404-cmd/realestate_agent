import asyncio
import pandas as pd

from scraper.japan.realestate.xpaths import EXPIRED
from scraper.core.base_scraper import BaseScraper
from scraper.japan.realestate.data_extractor import extract_static_dom_data
from scraper.japan.realestate.clean_data import clean_and_normalize_dict

from manage_db.db_manager_v1 import DbManagerV1
from manage_db.image_db_manager import ImageDb

from utils.logger import get_logger

res_updater = get_logger("RealEstateReScraper","scraper")

class ReScrape(BaseScraper):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.db = DbManagerV1(table_name="jp_realestate_v1")
        self.db_img = ImageDb()

    async def update_card(self,listing_ids,urls,start_browser = True):
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
                    clean_data = clean_and_normalize_dict(new_data)

                    self.db.update_listing(listing_id,clean_data)
                    #print(f"{index} data : {clean_data}")

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

    def get_bad_id(self):
        # change this based on the issue of specific data
        query = """
        SELECT id , source_listing_id
        FROM jp_realestate_v1
        WHERE
            data ? 'Size'
            OR data ? 'Location'
            OR data ? 'Year Built'
            OR data ? 'Building Name'
            OR data ? 'Maintenance Fee';
        """
        engine = self.db.get_db_engine()
        df = pd.read_sql(query,engine)
        return df

    # doesnt scrape images
    async def continuous_update(self, interval_sec=5,batch_wise = False , max_batches = 1):
        await self.start_browser()

        BATCH_SIZE = 100

        try:
            while True:
                res_updater.info("Starting update cycle")

                df = self.get_bad_id()

                res_updater.info(f"{len(df.index)} rows to update")


                #make urls
                df["source_listing_id"] = df["source_listing_id"].apply(lambda source_id : f"https://realestate.co.jp/en/forsale/view/{source_id}")

                listing_ids = df["id"].tolist()
                urls = df["source_listing_id"].tolist()

                if not listing_ids or not urls:
                    res_updater.warning("No bad listing found")
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

                res_updater.info("re scrape cycle completed.")

        except KeyboardInterrupt:
            res_updater.exception("re scrape stopped by user")
        except Exception as e:
            res_updater.exception(f"Error {e}")

        finally:
            self.db.close_conn()
            await self.close_browser()

if __name__ == "__main__":
    updater = ReScrape(None,None)
    task = updater.continuous_update()
    asyncio.run(task)