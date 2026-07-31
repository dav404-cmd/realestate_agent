from pydantic import BaseModel, StrictBool
from typing import Optional

from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostRegressor

from ml_analysis.data_cleaning.data_preprocesser import DataPreprocess

class PropertyFeatures(BaseModel):
    balcony_size: float | None = None
    building_area_ratio: float | None = None

    city: str
    district: str

    floor_area_ratio: float | None = None
    gross_yield: float | None = None

    land_area: float | None = None
    land_rights: str

    maintenance_fee: float | None = None

    ns_distance_min: float | None = None
    ns_line: str
    ns_mode: str
    ns_name: str

    occupancy: str
    parking: str

    potential_annual_rent: float | None = None

    prefecture: str

    repair_reserve_fund: float | None = None

    size: float

    structure: str
    transaction_type: str
    type: str

    total_floors: float | None = None
    unit_floor: float | None = None

    year_built: float | None = None

    zoning: str

    is_whole_building: int = 0

    rooms: float | None = None

    has_living: bool
    has_dining: bool = False
    has_kitchen: bool = False
    has_storage: bool = False

    facing_north: bool = False
    facing_south: bool = False
    facing_east: bool = False
    facing_west: bool = False

    age: float | None = None

    days_until_available: float | None = None
    available_month: float | None = None
    available_year: float | None = None

class PropertyPredictor:
    def __init__(self):
        root = Path(__file__).parents[1].resolve()
        model_path = root / "models" / "catboost_real_estate.cbm"
        print(f"root : {root} , model path : {model_path}")
        self.model = CatBoostRegressor()
        self.model.load_model(
            str(model_path)
        )
        self.cleaner = DataPreprocess()

    def predict(self, features: PropertyFeatures):
        df = pd.DataFrame([features.model_dump()])

        # reorder to match the exact column order used at training time
        df = df[self.model.feature_names_]

        cat_features = self.model.get_cat_feature_indices()  # or keep explicit list
        for col in df.columns[cat_features]:
            df[col] = df[col].fillna("Unknown")

        pred_log = self.model.predict(df)[0]
        price = np.expm1(pred_log)
        return round(price)

if __name__ == "__main__":
    features = PropertyFeatures(
        # Basic
        size=128.69,
        prefecture="Tokyo",
        city="Meguro-ku",
        district="Nakameguro",

        # Property
        type="House",
        structure="Wood",
        transaction_type="Exclusive",

        # Land
        land_area=74.35,
        land_rights="Freehold",
        zoning="Residential",

        # Building
        year_built=2010,
        age=16,  # Assuming your dataset year is 2026
        total_floors=3,
        unit_floor=None,  # Detached house

        # Layout
        rooms=4,  # 4LDK
        has_living=True,
        has_dining=True,
        has_kitchen=True,
        has_storage=True,

        # Orientation
        facing_north=True,
        facing_south=True,
        facing_east=False,
        facing_west=True,

        # Ratios
        building_area_ratio=60.0,
        floor_area_ratio=150.0,

        # Balcony
        balcony_size=19.0,

        # Station
        ns_name="Yutenji",
        ns_line="Tokyu Toyoko Line",
        ns_mode="Walk",
        ns_distance_min=11,

        # Status
        occupancy="Occupied",
        parking="Available",

        # Financial
        maintenance_fee=None,
        repair_reserve_fund=None,
        gross_yield=None,
        potential_annual_rent=None,

        # Availability
        available_year=2026,
        available_month=10,
        days_until_available=None,

        # Other
        is_whole_building=1
    )
    pred_model = PropertyPredictor()
    res = pred_model.predict(features)
    print(res)