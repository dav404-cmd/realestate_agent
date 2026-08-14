import asyncio

from fastapi import APIRouter, BackgroundTasks,status

from scraper.japan.realestate.runner import RealestateScraperRunner
from scraper.japan.realestate.updater import UpdateRealEstate
from scraper.japan.realestate.metadataupdater import MetaDataUpdater

from utils.logger import get_logger

scp_log = get_logger("ScraperApi" , "api")
router = APIRouter()

@router.post("/scrape_listing",status_code=status.HTTP_202_ACCEPTED)
def scrape_listing(background_task : BackgroundTasks, building_type=None,max_page: int = 5):
    scp_log.info(f"starting scraper with args building type = {building_type} , max_page = {max_page}")
    scraper = RealestateScraperRunner()

    def run_scraper():
        task = scraper.run(building_type=building_type,max_pages=max_page)
        asyncio.run(task)
        scp_log.info(f"scraping completed for {max_page} pages")

    background_task.add_task(run_scraper)
    return {"message" : "scraper started in the background."}

@router.post("/status_update",status_code=status.HTTP_202_ACCEPTED)
def update_status(background_task : BackgroundTasks ,batch_wise:bool=True ,max_batches : int = 1):
    scp_log.info("starting status update")
    status_updater = UpdateRealEstate()
    def run_status_updater():
        task = status_updater.continuous_update(batch_wise=batch_wise,max_batches=max_batches)
        asyncio.run(task)
        scp_log.info(f"Status update completed for {max_batches} batches")

    background_task.add_task(run_status_updater)
    return {"message":"status updater started in the background"}


@router.post("/metadata_update", status_code=status.HTTP_202_ACCEPTED)
def update_metadata(background_task: BackgroundTasks, batch_wise: bool = True, max_batches: int = 1):
    scp_log.info("starting metadata update")
    status_updater = MetaDataUpdater()

    def run_status_updater():
        task = status_updater.continuous_update(batch_wise=batch_wise, max_batches=max_batches)
        asyncio.run(task)
        scp_log.info(f"Metadata update completed for {max_batches} batches")

    background_task.add_task(run_status_updater)
    return {"message": "metadata updater started in the background"}

# --For airflow--
@router.post("/scrape_listing_af", status_code=status.HTTP_200_OK)
async def scrape_listing_af(
    building_type=None,
    max_page: int = 5
):
    scp_log.info(
        f"Starting Airflow scraper with args "
        f"building type={building_type}, max_page={max_page}"
    )

    scraper = RealestateScraperRunner()

    await scraper.run(
        building_type=building_type,
        max_pages=max_page
    )

    scp_log.info(
        f"Airflow scraper completed for {max_page} pages"
    )

    return {
        "message": "scraper completed",
        "max_pages": max_page
    }


@router.post("/status_update_af", status_code=status.HTTP_200_OK)
async def update_status_af(
    batch_wise: bool = True,
    max_batches: int = 1
):
    scp_log.info("Starting Airflow status update")

    status_updater = UpdateRealEstate()

    await status_updater.continuous_update(
        batch_wise=batch_wise,
        max_batches=max_batches
    )

    scp_log.info(
        f"Status update completed for {max_batches} batches"
    )

    return {
        "message": "status update completed",
        "max_batches": max_batches
    }


@router.post("/metadata_update_af", status_code=status.HTTP_200_OK)
async def update_metadata_af(
    batch_wise: bool = True,
    max_batches: int = 1
):
    scp_log.info("Starting Airflow metadata update")

    metadata_updater = MetaDataUpdater()

    await metadata_updater.continuous_update(
        batch_wise=batch_wise,
        max_batches=max_batches
    )

    scp_log.info(
        f"Metadata update completed for {max_batches} batches"
    )

    return {
        "message": "metadata update completed",
        "max_batches": max_batches
    }