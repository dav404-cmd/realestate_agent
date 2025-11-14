import asyncio

from scraper.japan.realestate.logic import RealestateScraperLogic
from utils.logger import get_logger

res_log = get_logger("RealestateScraper")

class RealestateScraperRunner:
    def __init__(self):
        self.scraper = RealestateScraperLogic()

    # The main runner function.
    async def run(self,building_type = "house"):
        await self.scraper.start_browser()
        try:

            url = f"https://realestate.co.jp/en/forsale?building_type={building_type}"

            ids = await self.scraper.get_cards_id(url)

            urls = await self.scraper.make_url(ids)

            data = await self.scraper.collect_data(urls)

            await self.scraper.store_csv(data,"real_estate")

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