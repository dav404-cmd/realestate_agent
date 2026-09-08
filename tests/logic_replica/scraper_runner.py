import asyncio

from scraper.japan.realestate.logic import RealestateScraperLogic
from utils.logger import get_logger

res_log = get_logger("RealestateScraperReplica","test")

class RealestateScraperRunnerReplica:
    def __init__(self):
        self.scraper = RealestateScraperLogic("jp_realestate_v1", "realestate.co")


    # The main runner function.
    async def run(self,building_type = None,max_pages = 1):  #None = all property
        await self.scraper.start_browser(proxy_mode=False)

        page_no = 1
        session_seen_id = set()

        self.scraper.clear_json("real_estate")

        try:
            while page_no <= max_pages:

                res_log.info(f"scraping page {page_no}")

                if not building_type:
                    url = f"https://realestate.co.jp/en/forsale?order=date_entered_ranking-desc&page={page_no}"
                else:
                    url = f"https://realestate.co.jp/en/forsale?building_type={building_type}&order=date_entered_ranking-desc&page=1"

                ids = await self.scraper.get_cards_id(url)

                if len(ids) == 0:
                    res_log.warning(f"{len(ids)} ids in page , retrying page : {url}.")
                    ids = await self.scraper.get_cards_id(url)
                    if len(ids) == 0:
                        res_log.warning(f"No cards in {url}; stopping.")
                        break

                data = await self.scraper.collect_data(ids,session_seen_id)

                self.scraper.store_json(data,file_name="real_estate")

                page_no += 1

                return ids , data

        except Exception as e:
            res_log.error(f"Error :{e}")
        except KeyboardInterrupt:
            res_log.warning(f"scraper stopped by user.")
        finally:
            await self.scraper.close_browser()

