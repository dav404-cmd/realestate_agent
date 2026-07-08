import re
from utils.logger import get_logger

res_log = get_logger("RealestateExtractor")


async def extract_data(page):

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

        return data
    except Exception as e:
        res_log.error(f"error extracting : {e}")
        return None

IMAGE_SUFFIX_RE = re.compile(r"_w\d+_h\d+_c(?=\.(?:png|jpe?g)$)",re.IGNORECASE)

async def extract_image(page) -> list:
    try :
        await page.wait_for_selector("div#js-rej-img-thumbnails", timeout=10000)
        stc_image = await page.locator("div.detail-item.text-center img").get_attribute("src")
        images_src = await page.locator("a.thumbnail img").evaluate_all(
            "(els) => els.map(el => el.getAttribute('src'))"
        )

        images_src = ([stc_image] if stc_image else []) + images_src
        images_src = list(dict.fromkeys(images_src))
        if not images_src:
            res_log.warning("Listing has no images")
        return images_src
    except Exception as e :
        res_log.exception(f"Error during image_extraction {e}")
        return []

async def extract_listing(page):
    data = await extract_data(page)
    if data is None:
        return None
    data["images"] = await extract_image(page)
    return data

