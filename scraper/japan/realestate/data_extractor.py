import re
import asyncio

from utils.logger import get_logger

res_log = get_logger("RealestateExtractor","scraper")

import asyncio
import re

# Cleaner regex to capture any width/height suffix like _w300 or _w150
IMAGE_SUFFIX_RE = re.compile(r"_(?:w\d+|h\d+)(?:_c)?(?=\.(?:png|jpe?g|webp)$)", re.IGNORECASE)


async def extract_static_dom_data(page) -> dict: #todo : fix extraction in features -> Refrigerator / Freezer and list dubs (delete all list with features for now.).
    """
    Executes a single JavaScript block inside the browser to extract
    all text data instantly. Zero cross-talk lag between Python and Playwright.
    """
    try:
        data = await page.evaluate("""() => {
            const result = {};
            const trimText = (el) => el ? el.innerText.trim() : null;

            // 1. Location
            const locEl = document.querySelector('h4.text-xl');
            if (locEl) result['Location'] = locEl.innerText.trim();

            // 2. Size and Type
            document.querySelectorAll('.property-details').forEach(el => {
                const title = el.querySelector('.property-details-title');
                const content = el.querySelector('.property-details-content');
                if (title && content) result[title.innerText.trim()] = content.innerText.trim();
            });

            // 3. Available From Date
            const dateNodes = Array.from(document.querySelectorAll('span'));
            const availNode = dateNodes.find(el => el.innerText.includes('Available From:'));
            if (availNode && availNode.nextElementSibling) {
                result['Available From'] = availNode.nextElementSibling.innerText.trim();
            }

            // 4. Price & Additional Specs (Land Area, Land Rights, etc.)
            document.querySelectorAll('.property-additional-details').forEach(el => {
                const title = el.querySelector('.property-additional-details-title');
                const content = el.querySelector('.property-additional-details-content');
                if (title && content) result[title.innerText.trim()] = content.innerText.trim();
            });

            // 5. Descriptions (Targets un-classed divs safely using H4 text headings)
            const h4s = Array.from(document.querySelectorAll('h4.font-semibold.text-2xl'));

            const descH4 = h4s.find(h4 => h4.innerText.includes('Building Description'));
            if (descH4 && descH4.nextElementSibling) {
                result['Description'] = descH4.nextElementSibling.innerText.trim();
            }

            const propDescH4 = h4s.find(h4 => h4.innerText.includes('Property Description'));
            if (propDescH4 && propDescH4.nextElementSibling) {
                result['Property Description'] = propDescH4.nextElementSibling.innerText.trim();
            }

            // 6. Date Updated
            const updatedH4 = h4s.find(h4 => h4.innerText.includes('Date Updated'));
            if (updatedH4 && updatedH4.nextElementSibling) {
                result['Date Updated'] = updatedH4.nextElementSibling.innerText.trim();
            }

            // 7. Transportation (Extracting ONLY the first, closest item)
            let station = null, walk = null;
            const candidates = Array.from(document.querySelectorAll('.grid.gap-1'));
            
            for (const container of candidates) {
                const firstDiv = container.querySelector(':scope > div');
                if (!firstDiv) continue;
            
                const nameEl = firstDiv.querySelector('.font-semibold');
                const walkEl = firstDiv.querySelector('li.has-icon');
            
                if (nameEl && walkEl && nameEl.innerText.includes('Station')) {
                    station = nameEl.innerText.trim();
                    walk = walkEl.innerText.trim();
                    break;
                }
            }
            
            result['ns_raw_name'] = station;
            result['ns_raw_time'] = walk;
            
            // 8. Features
            const featureSet = new Set();
            document.querySelectorAll('div.border.bg-white.border-gray-200.rounded-lg').forEach(el => {
                const clone = el.cloneNode(true);
                clone.querySelectorAll('style, svg').forEach(node => node.remove()); // strip icon SVG/CSS noise
                const text = clone.innerText.trim();
                if (text) featureSet.add(text);
            });
            if (featureSet.size > 0) result['Features'] = Array.from(featureSet);

            // 9. Agent Name
            const agentEl = document.querySelector('.card.max-w-sm .card-title');
            if (agentEl) result['Agent'] = agentEl.innerText.trim();

            return result;
        }""")
        return data
    except Exception as e:
        res_log.error(f"error extracting static data via evaluate: {e}")
        return {}


async def extract_images_via_overlay(page) -> list:
    """
    Clicks the thumbnail, handles the overlay layout safely, and scrapes
    all high-res target source URLs.
    """
    images_src = []
    try:
        # 1. Click the first image figure container to pop open the modal
        overlay_trigger = page.locator("figure.cursor-pointer, button.shrink-0.border-2").first
        if await overlay_trigger.count() > 0:
            await overlay_trigger.click()

            # 2. Wait until the target image thumbnail buttons load inside the overlay
            await page.wait_for_selector("button.shrink-0 img", timeout=5000)

            # 3. Pull all image sources at once via evaluate_all
            images_src = await page.locator("button.shrink-0 img").evaluate_all(
                "(els) => els.map(el => el.getAttribute('src'))"
            )

            # 4. Strip out sizing modifications (_w150, _w300) to grab original full-size asset
            images_src = [IMAGE_SUFFIX_RE.sub("", img) for img in images_src if img]
            images_src = list(dict.fromkeys(images_src))  # Keep unique

        if not images_src:
            res_log.warning("Listing has no images via overlay extraction")
        return images_src

    except Exception as e:
        res_log.error(f"Error during image_extraction via overlay: {e}")
        return []


async def extract_listing(page) -> dict:
    """
    The orchestrator function. Ensures everything runs sequentially in an
    un-interrupted timeline.
    """
    try:
        # Wait for the baseline node layout to settle down
        await page.wait_for_selector("h4.text-xl, .property-details", timeout=10000)
    except Exception:
        res_log.error("Target elements not found on page within timeout.")
        return {}

    combined_result = {}

    # Step 1: Run static parser. Total separation from active clicks means 0% race conditions.
    static_data = await extract_static_dom_data(page)
    combined_result.update(static_data)

    # Step 2: Trigger click event context shift and gather photos cleanly
    combined_result["images"] = await extract_images_via_overlay(page)

    return combined_result
