import asyncio
import re

from scraper.core.base_scraper import BaseScraper
from scraper.japan.realestate.xpaths import CARDS,DETAILS_LINK,INFO_TABLE
from scraper.japan.realestate.data_extractor import extract_data,clean_all_listings

class RealestateScraper(BaseScraper):

    @staticmethod
    async def make_url(ids : list) -> list:
        urls = []
        for id in ids:
            url = f"https://realestate.co.jp/en/forsale/view/{id}"
            urls.append(url)
        return urls


    async def get_cards_id(self,url):
        await self.main_page.goto(url)
        cards = await self.main_page.query_selector_all(CARDS)
        print(f"found {len(cards)} cards")
        ids = []
        for card in cards:
            link = await card.query_selector(DETAILS_LINK)
            if link:
                href = await link.get_attribute('href')
                match = re.search(r'/view/(\d+)',href)
                if match:
                    ids.append(match.group(1))
            else:
                print("link not found.")
        print("found ids")
        print(ids)
        return ids

    async def collect_data(self, urls):

        scraped_results = []

        async def handle_page(url, index):
            page = await self.context.new_page()

            async def page_closer():
                await page.close()

            try:
                await page.goto(url, wait_until="networkidle", timeout=60000)
                print(f"[{index}] Opened: {url}")

                await page.wait_for_selector(INFO_TABLE, timeout=15000)
                data = await extract_data(page, page_closer)

                if data:
                    data["url"] = url
                    scraped_results.append(data)
                else:
                    print(f"[{index}] No data extracted: {url}")

            except Exception as e:
                print(f"[{index}] Error scraping {url}: {e}")
                await page_closer()

        # Limit concurrency (to avoid hitting the site too hard)
        sem = asyncio.Semaphore(5)

        async def limited_task(i, url):
            async with sem:
                await handle_page(url, i)

        await asyncio.gather(*(limited_task(i, url) for i, url in enumerate(urls)))

        print(f"* Done scraping {len(scraped_results)} pages.")
        clean_scraped_results = clean_all_listings(scraped_results)
        print(clean_scraped_results)
        return clean_scraped_results


    async def scraper(self,building_type = "house"):
        await self.start_browser()
        try:

            url = f"https://realestate.co.jp/en/forsale?building_type={building_type}"

            ids = await self.get_cards_id(url)

            urls = await self.make_url(ids)

            data = await self.collect_data(urls)

            await self.store_csv(data,"test")



        except Exception as e:
            print(f"[scraper] Error :{e}")
        except KeyboardInterrupt:
            print(f"scraper stopped by user.")
        finally:
            await self.close_browser()

if __name__ == "__main__":
    scrape = RealestateScraper()
    task = scrape.scraper()
    asyncio.run(task)
