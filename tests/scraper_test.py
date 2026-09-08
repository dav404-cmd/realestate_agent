import pytest
import pytest_asyncio

from pathlib import Path

import json

from scraper.japan.realestate.logic import RealestateScraperLogic
from tests.logic_replica.scraper_runner import RealestateScraperRunnerReplica

pytestmark = pytest.mark.integration

REQUIRED_LISTING_FIELDS = {
    "source_listing_id",
    "price_yen",
    "type",
    "prefecture",
    "city",
}

@pytest_asyncio.fixture
async def scraper():
    logic = RealestateScraperLogic("jp_realestate_v1", "realestate.co")
    await logic.start_browser()
    yield logic
    await logic.close_browser()

@pytest.mark.asyncio
async def test_get_cards(scraper):
    ids = await scraper.get_cards_id("https://realestate.co.jp/en/forsale?page=1")
    assert isinstance(ids, list)
    assert len(ids) > 0

@pytest.mark.asyncio
async def test_scraper_together():
    root = Path(__file__).parents[1].resolve()
    scraper_runner = RealestateScraperRunnerReplica()

    ids, scraped_data = await scraper_runner.run()

    # Basic scraper validation
    assert isinstance(ids, list)
    assert len(ids) > 0

    assert isinstance(scraped_data, list)
    assert len(scraped_data) > 0

    assert all(
        isinstance(listing, dict)
        for listing in scraped_data
    )


    # Listing schema validation

    for listing in scraped_data:
        assert REQUIRED_LISTING_FIELDS.issubset(listing.keys()), (
            f"Missing fields: {REQUIRED_LISTING_FIELDS - listing.keys()}"
        )

        assert isinstance(listing["source_listing_id"],str), f"source_listing_id must be str, got {type(listing['source_listing_id']).__name__}"
        assert isinstance(listing["price_yen"],int), f"price_yen must be int, got {type(listing['price_yen']).__name__}"
        assert isinstance(listing["images"],list), f"images must be list, got {type(listing['images']).__name__}"

        if listing.get("size") is not None:
            assert isinstance(
                listing["size"],
                (int, float)
            )
        if listing.get("gross_yield") is not None:
            assert isinstance(
                listing["gross_yield"],
                (int, float)
            )

    # JSON output validation

    json_path = (
        root
        / "data"
        / "raw"
        / "real_estate.json"
    )

    assert json_path.exists()

    with open(
        json_path,
        "r",
        encoding="utf-8-sig"
    ) as f:
        json_data = json.load(f)

    assert isinstance(json_data, list)
    assert len(json_data) > 0

    assert all(
        isinstance(listing, dict)
        for listing in json_data
    )
