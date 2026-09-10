import pytest
from pathlib import Path
import json

from scraper.japan.realestate.clean_data import clean_and_normalize_dict

def test_data_cleaner():
    test_dir = Path(__file__).parent.resolve()
    data_dir = test_dir / "util_data"
    print(f"data dir : {data_dir}")

    raw_data_file = data_dir / "raw_test.json"
    cleaned_data_file = data_dir / "clean_test.json"

    with open(raw_data_file, 'r' , encoding="utf-8-sig") as f :
        raw_data = json.load(f)
    with open(cleaned_data_file, 'r' , encoding="utf-8-sig") as f :
        clean_test_data = json.load(f)

    clean_data = clean_and_normalize_dict(raw_data)

    assert clean_data == clean_test_data , f"cleaning function is acting different from usual . Results of cleaner : \n{clean_data}"