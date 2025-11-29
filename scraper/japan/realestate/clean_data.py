import re
from utils.logger import get_logger
from data.data_cleaner.clean_date import normalize_date
res_log = get_logger("RealestateCleaner")


def normalize_key(key: str) -> str:
    if not isinstance(key, str):
        key = str(key)

    # Basic normalize
    key = key.strip().lower()

    # Replace spaces and hyphens with underscore
    key = re.sub(r"[ \-]+", "_", key)

    # Remove any characters that are NOT letters, numbers, or underscore
    key = re.sub(r"[^a-z0-9_]", "", key)

    # Remove repeated underscores
    key = re.sub(r"_+", "_", key)

    # Remove leading/trailing underscores
    key = key.strip("_")

    return key

def normalize_dict_keys(d: dict) -> dict:
    clean = {}
    for k, v in d.items():
        clean[normalize_key(k)] = v
    return clean


def clean_text(value: str) -> str:
    if value is None:
        return None

    # Remove only ZERO-WIDTH characters, safe for Japanese
    value = re.sub(r"[\u200b\u200c\u200d\u2060]", "", value)

    # Collapse whitespace but keep Japanese characters intact
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def try_parse_int(s):
    if not s:
        return None
    m = re.search(r"([\d,]+)", s)
    if m:
        try:
            return int(m.group(1).replace(",", ""))
        except:
            return None
    return None


def try_parse_float(s):
    if not s:
        return None
    m = re.search(r"([\d,]+(?:\.\d+)?)", s)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except:
            return None
    return None


def try_parse_currency(s):
    if not s:
        return None

    m = re.search(r"(¥|JPY)\s*([\d,]+)", s)
    if m:
        try:
            return int(m.group(2).replace(",", ""))
        except:
            return None

    return try_parse_int(s)


def try_parse_m2(s):
    if not s:
        return None

    m = re.search(r"([\d,]+(?:\.\d+)?)\s*(m²|m2|sqm)", s, flags=re.I)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except:
            return None

    return None


def try_parse_percentage(s):
    if not s:
        return None

    m = re.search(r"([\d\.]+)\s*%", s)
    if m:
        try:
            return float(m.group(1))
        except:
            return None

    return None


def clean_value(key, value):
    v = clean_text(value)

    # ----- NUMERIC KEYS ONLY -----
    numeric_like = [
        "price", "rent", "fee", "maintenance", "expense", "tax",
        "size", "land_area", "floor_area", "building_area",
        "potential_annual_rent", "yield", "ratio", "road_width",
        "year_built", "built", "completed"
    ]

    # Currency
    if any(n in key for n in ["price", "rent", "fee", "annual"]):
        parsed = try_parse_currency(v)
        if parsed is not None:
            return parsed

    # m² area
    if any(n in key for n in ["m2", "sqm", "size", "area"]):
        parsed = try_parse_m2(v)
        if parsed is not None:
            return parsed

    # Percent ratios
    if any(n in key for n in ["yield", "ratio", "percentage"]):
        parsed = try_parse_percentage(v)
        if parsed is not None:
            return parsed

    # Year-like (only if key suggests year)
    if "year" in key or "built" in key:
        if re.fullmatch(r"\d{4}", v):
            return int(v)

    # General numeric values ONLY if the key suggests numeric meaning
    if any(n in key for n in numeric_like):
        num = try_parse_float(v)
        if num is not None:
            return int(num) if num.is_integer() else num

    # ----- TEXT FIELDS (building name, address, etc.) -----
    return v

def customize_listing(cleaned_dict: dict):
    KEY_MAP = {
        "price": "price_yen"
    }
    TRANSFORM = {
        "available_from" : normalize_date,
        "date_updated" : normalize_date,
        "next_update_schedule" : normalize_date
    }

    final = {}

    for clean_key, clean_value in cleaned_dict.items():

        if clean_key in TRANSFORM:
            clean_value = TRANSFORM[clean_key](clean_value)

        # If key is mapped → rename it
        if clean_key in KEY_MAP:
            final_key = KEY_MAP[clean_key]
            final[final_key] = clean_value

        # If key is NOT mapped → keep it unchanged
        else:
            final[clean_key] = clean_value

    return final


def clean_and_normalize_dict(raw: dict) -> dict:
    """Normalize keys THEN clean values."""
    normalized = normalize_dict_keys(raw)
    cleaned = {}

    for k, v in normalized.items():
        cleaned[k] = clean_value(k, v)

    mapped = customize_listing(cleaned)

    return mapped


def clean_all_listings(data_list):
    cleaned = []
    for item in data_list:
        try:
            cleaned.append(clean_and_normalize_dict(item))
        except Exception as e:
            res_log.error(f"Cleaning error for item: {e}")
    return cleaned

if __name__ == "__main__":
    data_list = {'Price': '¥105,800,000', 'Building Name': '🔸S111 MATSUBARA 3LDK HOUSE🔸', 'Floors': '3F', 'Available From': 'Apr 7, 2025', 'Type': 'House', 'Size': '99.02 m²', 'Land Area': '72.00 m²', 'Land Rights': 'Freehold', 'Location': 'Akatsutsumi, Setagaya-ku, Tokyo', 'Occupancy': 'Vacant', 'Nearest Station': 'Matsubara Station (4 min. walk)\nTōkyū Setagaya Line', 'Layout': '3LDK', 'Construction Completed': 'April 2018', 'Direction Facing': 'West', 'Transaction Type': 'Brokerage', 'Floor Area Ratio': '200.0%', 'Building Area Ratio': '60.0%', 'Zoning': 'Residential', 'Road Width': '4.00 m', 'Structure': 'Wood', 'Building Description': "Looking for an English-speaking real estate broker in Tokyo?\n\nWhether you're overseas or in Tokyo, I provide professional, accurate advice as a licensed real estate broker specializing in luxury homes across the Tokyo Metropolitan area. I work with both international and local buyers and sellers, ensuring a seamless experience.\n\nWith bilingual and bicultural expertise, including experience as an agent in New York, I understand the needs of clients from diverse backgrounds.\n\nAll communication and assistance are in English, making the process smooth and stress-free.\n\nFor reliable guidance and exceptional service, feel free to contact me anytime to get started.\n\n🔹Licensed Real Estate Broker🔹\nAki Shimizu, RE/MAX Top Agent\n090-4677-7502\naki@topagent-tokyo.com\nFind out who I am more on topagent-tokyo.com", 'Other Expenses': '🔸What is the purchase cost?\n・Cash Purchase: Approx. 5-6% of the sale price\n・Loan Purchase: Approx. 7% of the sale price\n\n🔸Looking for financing? Feel free to call, text, or email me anytime.\n*Financing is available only to working residents. (PR holders: Up to 100% loan, Visa holders: A 20-30% down payment is required)', 'Landmarks': '・Gotokuji Temple\n・Setagaya Hachimangu Shrine\n・Hanegi Park', 'Parking': 'Available', 'Date Updated': 'Oct 23, 2025', 'Next Update Schedule': 'Nov 22, 2025', 'url': 'https://realestate.co.jp/en/forsale/view/1212976'}, {'Price': '¥320,000,000', 'Building Name': '鎌倉市長谷２丁目プール付き戸建', 'Floors': '3F', 'Available From': 'Mid Oct 2025', 'Type': 'House', 'Size': '229.15 m²', 'Land Area': '362.82 m²', 'Land Rights': 'Freehold', 'Location': 'Hase, Kamakura-shi, Kanagawa', 'Occupancy': 'Vacant', 'Nearest Station': 'Yuigahama Station (4 min. walk)\nEnoshima Electric Railway', 'Layout': '5LDK', 'Construction Completed': 'April 2009', 'Direction Facing': 'South', 'Transaction Type': 'Non-Exclusive', 'Floor Area Ratio': '150.0%', 'Building Area Ratio': '60.0%', 'Zoning': 'Residential', 'Structure': 'Wood', 'Building Description': 'Located in a residential area of \u200b\u200bthe historic city of Kamakura, this residence offers abundant natural light and ventilation.\n\nFeatures\n■ 6.5m x 2.7m swimming pool (maximum depth 1.27m)\n■ Rooftop offers stunning views of the sea, mountains, and Hasedera Temple.\n■ Rooftop terrace with jacuzzi\n■ Rooftop equipped with solar panels and opening skylights\n■ Living room with vaulted ceiling\n■ Living room with fireplace and underfloor heating\n■ Living room with fully-opening windows\n■ 3 bathrooms and 3 toilets', 'Other Expenses': '-', 'Parking': 'Available', 'Date Updated': 'Oct 20, 2025', 'Next Update Schedule': 'Jan 18, 2026', 'url': 'https://realestate.co.jp/en/forsale/view/1285594'}, {'Price': '¥535,000,000', 'Building Name': 'SUPERB HOSPITALITY HOUSE', 'Floors': '2F', 'Available From': 'Please Inquire', 'Type': 'House', 'Size': '686.73 m²', 'Land Area': '789.66 m²', 'Land Rights': 'Freehold', 'Gross Yield': '6.50%', 'Location': 'Midorigaokacho, Ashiya-shi, Hyogo', 'Occupancy': 'Occupied', 'Nearest Station': 'Ashiya Station (10 min. walk)\nJR Kōbe Line (Ōsaka-Kōbe)', 'Layout': 'Whole Building', 'Year Built': '2017', 'Direction Facing': 'South', 'Potential Annual Rent': '¥29,400,000 / year', 'Transaction Type': 'Seller', 'Floor Area Ratio': '200.0%', 'Building Area Ratio': '60.0%', 'Zoning': 'Residential', 'Road Width': '6.21 m', 'Structure': 'Steel Frame', 'Building Description': "●A popular area where asset value does not decline (ideal for owning as a second home)\n●Land price alone is 3,755 million yen (reference to surrounding land transactions), with a unit price of 1.57 million yen per tsubo.\n●No large-sized land is available in the area.\n●A relatively flat road, which is rare in the prime area of Ashiya City.\n●Currently rented at 2.45 million yen per month (yielding 6.53%) with an automatic renewal contract for a 3-year period.\n●There is a vacant house on the property suitable for two households (also possible to rent for 180,000 to 200,000 yen per month).\n●It's possible to operate as a guesthouse while living there.\n●A meticulously crafted building that cost 320 million yen seven years ago.\n●A 35-minute drive to the Osaka Expo and Integrated Resort (IR) venue.\n●Excellent access to Osaka and Kobe.\n●Located in an upscale residential area.", 'Parking': 'Available', 'Date Updated': 'Oct 22, 2025', 'Next Update Schedule': 'Nov 21, 2025', 'url': 'https://realestate.co.jp/en/forsale/view/1085035'}

    clean_data = clean_all_listings(data_list)
    print(clean_data)