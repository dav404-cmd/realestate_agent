import asyncio
import re

from scraper.core.base_scraper import BaseScraper
from scraper.japan.realestate.xpaths import CARDS,DETAILS_LINK,INFO_TABLE
from scraper.japan.realestate.data_extractor import extract_data
from scraper.japan.realestate.clean_data import clean_all_listings

from utils.logger import get_logger

res_log = get_logger("RealestateScraper")

class RealestateScraperLogic(BaseScraper):

    @staticmethod
    async def make_url(ids : list,session_seen_id : set) -> list:
        listings = []
        for id in ids:
            if id not in session_seen_id:
                listings.append({
                    "listing_id" : id,
                    "url" : f"https://realestate.co.jp/en/forsale/view/{id}"
                })

                session_seen_id.add(id)
            else:
                res_log.info(f"auto ignored {id}")
        return listings


    async def get_cards_id(self,url):
        await self.main_page.goto(url, wait_until="domcontentloaded")
        cards = await self.main_page.query_selector_all(CARDS)
        res_log.info(f"found {len(cards)} cards")
        ids = []
        for card in cards:
            link = await card.query_selector(DETAILS_LINK)
            if link:
                href = await link.get_attribute('href')
                match = re.search(r'/view/(\d+)',href)
                if match:
                    ids.append(match.group(1))
            else:
                res_log.error("link not found.")
        res_log.info("found ids")
        return ids

    async def collect_data(self,ids:list,session_seen_id:set):
        listing = await self.make_url(ids,session_seen_id)

        scraped_results = []

        async def handle_page(item, index):
            page = await self.context.new_page()

            async def page_closer():
                await page.close()

            try:
                url = item['url']
                listing_id = item['listing_id']
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                res_log.info(f"[{index}] Opened: {url}")

                await page.wait_for_selector(INFO_TABLE, timeout=15000)
                data = await extract_data(page, page_closer)

                if data:
                    data["source_listing_id"] = listing_id
                    scraped_results.append(data)
                else:
                    res_log.warning(f"[{index}] No data extracted: {url}")

            except KeyboardInterrupt:
                res_log.warning("process stopped by the user.")

            except Exception as e:
                res_log.error(f"[{index}] Error scraping {url}: {e}")
                await page_closer()

        # Limit concurrency (to avoid hitting the site too hard)
        sem = asyncio.Semaphore(5)

        async def limited_task(i, item):
            async with sem:
                await handle_page(item, i )

        await asyncio.gather(*(limited_task(i, item) for i, item in enumerate(listing)))

        res_log.info(f"* Done scraping {len(scraped_results)} pages.")
        clean_scraped_results = clean_all_listings(scraped_results)
        return clean_scraped_results