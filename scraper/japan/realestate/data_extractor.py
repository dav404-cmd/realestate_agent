import re
from utils.logger import get_logger

res_log = get_logger("RealestateExtractor")

def clean_listing_block(raw_text: str):
    data = {}
    lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

    current_key = None
    for line in lines:
        # If the line looks like a "key: value"
        if ': ' in line:
            key, value = line.split(': ', 1)
            current_key = key.strip()
            data[current_key] = value.strip()
        else:
            # Append multiline values (like building descriptions)
            if current_key:
                data[current_key] += " " + line.strip()

    # normalize yen values to numbers
    for k, v in data.items():
        if '¥' in v or 'JPY' in v:
            # Find all numeric currency values
            matches = re.findall(r'(?:¥|JPY)\s?([\d,]+(?:\.\d+)?)', v)
            if matches:
                # Convert first match to int
                try:
                    data[k] = int(matches[0].replace(',', ''))
                except ValueError:
                    data[k] = None

    # normalize float values for m²
    for k in ['Size', 'Land Area']:
        if k in data:
            num = re.sub(r'[^\d.]', '', data[k])
            data[k] = float(num) if num else None

    # remove weird chars, unify case
    clean_data = {k.strip(): v for k, v in data.items()}

    return clean_data

def dict_to_raw_text(data_dict):
    lines = []
    for k, v in data_dict.items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines)


def clean_all_listings(data_list):
    cleaned = []
    for item in data_list:
        raw_text = dict_to_raw_text(item)
        cleaned_item = clean_listing_block(raw_text)
        cleaned.append(cleaned_item)
    return cleaned

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
    finally:
        await browser_closer()

if __name__ == "__main__":
    raw_txt = """Unit Number: -
    Price: ¥368,000,000
    Building Name: Karuizawa Sengataki Villa Area Nishiku Shin-Karamatsunomori A
    Floors: 1F
    Available From: Please Inquire
    Type: House
    Size: 269.12 m²
    Land Area: 1,508.00 m²
    Land Rights: Freehold
    Maintenance Fee: ¥20,416 / mth
    Location: Nagakura, Kitasaku-gun Karuizawa-machi, Nagano
    Nearest Station: Nakakaruizawa Station (15 min. by car)
    Shinano Railway Line
    Layout: 4LDK
    Year Built: 2025
    Direction Facing: South
    Transaction Type: Non-Exclusive
    Zoning: Residential
    Structure: Wood
    Unit Summary: Newly-built house
    Building Description: Electricity Chubu Electric Power Co., Inc.
    Gas No gas
    Water Private water supply system
    Hot Water Kerosene powered water heating system
    Drain Septic tank (Individual system)
    Sewage Septic tank
    Air Conditioner Wood stove (01 unit)
    Car Park Built-in garage (1 car), car space (2 cars) available
    Other Expenses: Total Management Fee(monthly) JPY 20,416
    Breakdown
    Common Area Maintenance fee JPY 216,480/Annual
    Water basic charge JPY 18,480/Annual
    Water meter charge JPY 3,432/Annual
    Sewage treatment fee (up to 35 cubic meters of water per year) JPY 6,600/Annual
    
    
    Contract Stamp Fee JPY 60,000
    Brokerage Fee JPY 12,210,000
    Remarks The water usage fee is included in the basic water fee up to 35 cbm. If the usage exceeds 35 cbm, 33 yen (tax included) will be added for every 1 cbm.
    ※Contract Stamp Fee and Brokerage Fee are subject to change depending on the actual sales price.
    ※Property tax for the year of sale will be allocated to Seller and Buyer based on the delivery date.
    Parking: Available
    Date Updated: Nov 11, 2025
    Next Update Schedule: Dec 11, 2025"""
    clean_txt = clean_listing_block(str(raw_txt))
    print(clean_txt)

    data_list = {'Price': '¥105,800,000', 'Building Name': '🔸S111 MATSUBARA 3LDK HOUSE🔸', 'Floors': '3F', 'Available From': 'Apr 7, 2025', 'Type': 'House', 'Size': '99.02 m²', 'Land Area': '72.00 m²', 'Land Rights': 'Freehold', 'Location': 'Akatsutsumi, Setagaya-ku, Tokyo', 'Occupancy': 'Vacant', 'Nearest Station': 'Matsubara Station (4 min. walk)\nTōkyū Setagaya Line', 'Layout': '3LDK', 'Construction Completed': 'April 2018', 'Direction Facing': 'West', 'Transaction Type': 'Brokerage', 'Floor Area Ratio': '200.0%', 'Building Area Ratio': '60.0%', 'Zoning': 'Residential', 'Road Width': '4.00 m', 'Structure': 'Wood', 'Building Description': "Looking for an English-speaking real estate broker in Tokyo?\n\nWhether you're overseas or in Tokyo, I provide professional, accurate advice as a licensed real estate broker specializing in luxury homes across the Tokyo Metropolitan area. I work with both international and local buyers and sellers, ensuring a seamless experience.\n\nWith bilingual and bicultural expertise, including experience as an agent in New York, I understand the needs of clients from diverse backgrounds.\n\nAll communication and assistance are in English, making the process smooth and stress-free.\n\nFor reliable guidance and exceptional service, feel free to contact me anytime to get started.\n\n🔹Licensed Real Estate Broker🔹\nAki Shimizu, RE/MAX Top Agent\n090-4677-7502\naki@topagent-tokyo.com\nFind out who I am more on topagent-tokyo.com", 'Other Expenses': '🔸What is the purchase cost?\n・Cash Purchase: Approx. 5-6% of the sale price\n・Loan Purchase: Approx. 7% of the sale price\n\n🔸Looking for financing? Feel free to call, text, or email me anytime.\n*Financing is available only to working residents. (PR holders: Up to 100% loan, Visa holders: A 20-30% down payment is required)', 'Landmarks': '・Gotokuji Temple\n・Setagaya Hachimangu Shrine\n・Hanegi Park', 'Parking': 'Available', 'Date Updated': 'Oct 23, 2025', 'Next Update Schedule': 'Nov 22, 2025', 'url': 'https://realestate.co.jp/en/forsale/view/1212976'}, {'Price': '¥320,000,000', 'Building Name': '鎌倉市長谷２丁目プール付き戸建', 'Floors': '3F', 'Available From': 'Mid Oct 2025', 'Type': 'House', 'Size': '229.15 m²', 'Land Area': '362.82 m²', 'Land Rights': 'Freehold', 'Location': 'Hase, Kamakura-shi, Kanagawa', 'Occupancy': 'Vacant', 'Nearest Station': 'Yuigahama Station (4 min. walk)\nEnoshima Electric Railway', 'Layout': '5LDK', 'Construction Completed': 'April 2009', 'Direction Facing': 'South', 'Transaction Type': 'Non-Exclusive', 'Floor Area Ratio': '150.0%', 'Building Area Ratio': '60.0%', 'Zoning': 'Residential', 'Structure': 'Wood', 'Building Description': 'Located in a residential area of \u200b\u200bthe historic city of Kamakura, this residence offers abundant natural light and ventilation.\n\nFeatures\n■ 6.5m x 2.7m swimming pool (maximum depth 1.27m)\n■ Rooftop offers stunning views of the sea, mountains, and Hasedera Temple.\n■ Rooftop terrace with jacuzzi\n■ Rooftop equipped with solar panels and opening skylights\n■ Living room with vaulted ceiling\n■ Living room with fireplace and underfloor heating\n■ Living room with fully-opening windows\n■ 3 bathrooms and 3 toilets', 'Other Expenses': '-', 'Parking': 'Available', 'Date Updated': 'Oct 20, 2025', 'Next Update Schedule': 'Jan 18, 2026', 'url': 'https://realestate.co.jp/en/forsale/view/1285594'}, {'Price': '¥535,000,000', 'Building Name': 'SUPERB HOSPITALITY HOUSE', 'Floors': '2F', 'Available From': 'Please Inquire', 'Type': 'House', 'Size': '686.73 m²', 'Land Area': '789.66 m²', 'Land Rights': 'Freehold', 'Gross Yield': '6.50%', 'Location': 'Midorigaokacho, Ashiya-shi, Hyogo', 'Occupancy': 'Occupied', 'Nearest Station': 'Ashiya Station (10 min. walk)\nJR Kōbe Line (Ōsaka-Kōbe)', 'Layout': 'Whole Building', 'Year Built': '2017', 'Direction Facing': 'South', 'Potential Annual Rent': '¥29,400,000 / year', 'Transaction Type': 'Seller', 'Floor Area Ratio': '200.0%', 'Building Area Ratio': '60.0%', 'Zoning': 'Residential', 'Road Width': '6.21 m', 'Structure': 'Steel Frame', 'Building Description': "●A popular area where asset value does not decline (ideal for owning as a second home)\n●Land price alone is 3,755 million yen (reference to surrounding land transactions), with a unit price of 1.57 million yen per tsubo.\n●No large-sized land is available in the area.\n●A relatively flat road, which is rare in the prime area of Ashiya City.\n●Currently rented at 2.45 million yen per month (yielding 6.53%) with an automatic renewal contract for a 3-year period.\n●There is a vacant house on the property suitable for two households (also possible to rent for 180,000 to 200,000 yen per month).\n●It's possible to operate as a guesthouse while living there.\n●A meticulously crafted building that cost 320 million yen seven years ago.\n●A 35-minute drive to the Osaka Expo and Integrated Resort (IR) venue.\n●Excellent access to Osaka and Kobe.\n●Located in an upscale residential area.", 'Parking': 'Available', 'Date Updated': 'Oct 22, 2025', 'Next Update Schedule': 'Nov 21, 2025', 'url': 'https://realestate.co.jp/en/forsale/view/1085035'}

    clean_data = clean_all_listings(data_list)
    print(clean_data)