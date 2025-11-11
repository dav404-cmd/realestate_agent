async def extract_data(page,browser_closer):

    # Wait for the info section to appear
    await page.wait_for_selector("dl.dl-horizontal-border", timeout=10000)

    try:
        print("found table")
        dts = await page.query_selector_all("dl.dl-horizontal-border dt")
        dds = await page.query_selector_all("dl.dl-horizontal-border dd")
        data = {}
        for dt, dd in zip(dts, dds):
            key = (await dt.inner_text()).strip()
            value = (await dd.inner_text()).strip()
            data[key] = value

        print("Extracted data:")
        for k, v in data.items():
            print(f"{k}: {v}")

        await browser_closer()
        return data
    except Exception as e:
        print(f"error extracting {e}")
        return None
    finally:
        await browser_closer()