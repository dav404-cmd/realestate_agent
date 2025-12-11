import asyncio

from scraper.japan.realestate.logic import RealestateScraperLogic
from utils.logger import get_logger

res_log = get_logger("RealestateScraper")

class RealestateScraperRunner:
    def __init__(self):
        self.scraper = RealestateScraperLogic()

    @staticmethod
    def check_last_page(previous_ids,ids,page_no):
        # Detect repeated pages (site looping last page)
        if previous_ids is not None and ids == previous_ids:
            res_log.warning(f"Page {page_no} repeated the last page → stopping.")
            return True
        else:
            return False

    # The main runner function.
    async def run(self,building_type = None,max_pages = 389):  #None = all property
        await self.scraper.start_browser()

        page_no = 145
        previous_ids = None

        try:
            while page_no <= max_pages:

                res_log.info(f"scraping page {page_no}")

                if not building_type:
                    url = f"https://realestate.co.jp/en/forsale?page={page_no}"
                else:
                    url = f"https://realestate.co.jp/en/forsale?building_type={building_type}&page={page_no}"

                ids = await self.scraper.get_cards_id(url)

                if len(ids) == 0:
                    res_log.warning(f"{len(ids)} ids in page , retrying page : {url}.")
                    ids = await self.scraper.get_cards_id(url)
                    if len(ids) == 0:
                        res_log.warning(f"No cards in {url}; stopping.")
                        break

                last_page = self.check_last_page(previous_ids,ids,page_no)
                if last_page:
                    break
                previous_ids = ids

                urls = await self.scraper.make_url(ids)

                data = await self.scraper.collect_data(urls)

                self.scraper.store_db("jp_realestate","realestate.co",data,create_table=False)
                self.scraper.store_json(data,file_name="real_estate")

                page_no += 1

        except Exception as e:
            res_log.error(f"Error :{e}")
        except KeyboardInterrupt:
            res_log.warning(f"scraper stopped by user.")
        finally:
            await self.scraper.close_browser()

if __name__ == "__main__":
    runner = RealestateScraperRunner()
    task = runner.run()
    asyncio.run(task)