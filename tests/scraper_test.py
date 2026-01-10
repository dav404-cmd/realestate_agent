import pytest
import pytest_asyncio
from scraper.japan.realestate.logic import RealestateScraperLogic

@pytest_asyncio.fixture
async def scraper():
    logic = RealestateScraperLogic()
    await logic.start_browser()
    yield logic
    await logic.close_browser()

@pytest.mark.asyncio
async def test_get_cards(scraper):
    ids = await scraper.get_cards_id("https://realestate.co.jp/en/forsale?page=1")
    assert isinstance(ids, list)
    assert len(ids) > 0

@pytest.mark.asyncio
async def test_data_extraction(scraper):
    ids = await scraper.get_cards_id("https://realestate.co.jp/en/forsale?page=1")
    urls = await scraper.make_url(ids, {1297687})
    data = await scraper.collect_data(urls)
    assert isinstance(data, list)
    assert all(isinstance(d, dict) for d in data)
    assert "price_yen" in data[0]