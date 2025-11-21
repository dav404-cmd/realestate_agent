import re
from utils.logger import get_logger

res_log = get_logger("RealestateExtractor")


async def extract_data(page,browser_closer):

    # Wait for the info section to appear
    await page.wait_for_selector("dl.dl-horizontal-border", timeout=10000)

    try:
        #res_log.info("found table")
        dts = await page.query_selector_all("dl.dl-horizontal-border dt")
        dds = await page.query_selector_all("dl.dl-horizontal-border dd")
        data = {}
        for dt, dd in zip(dts, dds):
            key = (await dt.inner_text()).strip()
            value = (await dd.inner_text()).strip()
            data[key] = value

        await browser_closer()
        return data
    except Exception as e:
        res_log.error(f"error extracting : {e}")
        return None

