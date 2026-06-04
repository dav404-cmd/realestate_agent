import pandas as pd
import numpy as np
import re
from datetime import datetime

from manage_db.db_manager_v1 import DbManagerV1

pd.set_option("display.max_columns", None)

class DataPreprocess:
    @staticmethod
    def drop_unnecessary(df) -> pd.DataFrame:
        df = df.drop(columns=[
                            "id",
                            "source",
                            "scraped_at",
                            "status",
                            "last_update",
                            "source_listing_id",
                            "building_description",
                            "building_name",
                            "date_updated",
                            "unit_number",
                            "unit_summary",
                            "next_update_schedule",
                            "other_expenses"
        ])
        return df

    @staticmethod
    def drop_difficult(df) -> pd.DataFrame:
        # Useful data currently unusable due to high non value.
        df = df.drop(columns = [
                                "investment_situation",
                                "road_width",
                                "sell_situation",
                                "landmarks",
                                "manager_style",
                                "manage_type"
        ])
        return df

    @staticmethod
    def clean_layout(df)->pd.DataFrame:
        # standardize to string
        df["layout"] = df["layout"].fillna("").astype(str).str.strip()

        # 1. Flag whole-building listings
        df["is_whole_building"] = df["layout"].str.contains("whole", case=False).astype(int)

        # 2. Extract number of rooms (LDK style)
        # e.g. 1LDK, 3DK, 2K → extract leading digits
        df["rooms"] = df["layout"].str.extract(r"^(\d+)").astype(float)

        # 3. Detect layout characters (L, D, K)
        df["has_living"] = df["layout"].str.contains("L", case=False).astype(int)
        df["has_dining"] = df["layout"].str.contains("D", case=False).astype(int)
        df["has_kitchen"] = df["layout"].str.contains("K", case=False).astype(int)
        df["has_storage"] = df["layout"].str.contains(r"S(?!TUDIO)", case=False).astype(int)

        # 5. Fill missing rooms for whole buildings with NaN (can't infer)
        df.loc[df["is_whole_building"] == 1, "rooms"] = np.nan

        df = df.drop(columns=["layout"])

        return df

    DIR_ANGLE = {
        "NORTH": 0,
        "NORTHEAST": 45,
        "EAST": 90,
        "SOUTHEAST": 135,
        "SOUTH": 180,
        "SOUTHWEST": 225,
        "WEST": 270,
        "NORTHWEST": 315
    }

    @staticmethod
    def clean_direction(df):
        directions = [
            "North",
            "South",
            "East",
            "West"
        ]

        for direction in directions:
            df[f"facing_{direction.lower()}"] = (
                df["direction_facing"]
                .fillna("")
                .str.contains(direction, regex=False)
                .astype(int)
            )

        df = df.drop(columns=["direction_facing"])
        return df

    @staticmethod
    def clean_dates(df) -> pd.DataFrame:
        current_year = datetime.now().year
        df["age"] = current_year - df['construction_completed']
        df["available_from"] = pd.to_datetime(df["available_from"], errors='coerce')

        # Days until available (NaN stays if missing)
        df['days_until_available'] = (pd.Timestamp.today() - df['available_from']).dt.days

        # Extract month and year for seasonality patterns
        df['available_month'] = df['available_from'].dt.month
        df['available_year'] = df['available_from'].dt.year

        df = df.drop(columns=["construction_completed","available_from"])
        return df

    @staticmethod
    def clean_cat_na(df):
        cat_features = [
            'city',
            'district',
            'land_rights',
            'ns_line',
            'ns_mode',
            'ns_name',
            'occupancy',
            'parking',
            'prefecture',
            'structure',
            'transaction_type',
            'type',
            'zoning'
        ]

        for col in cat_features:
            df[col] = df[col].fillna("Unknown")
            df[col] = df[col].fillna("Unknown")

        return df

    PIPELINE = [
        drop_unnecessary,
        drop_difficult,
        clean_dates,
        clean_layout,
        clean_direction,
        clean_cat_na
    ]
    def run_preprocessor(self,df):
        for step in self.PIPELINE:
            df = step(df)
        return df


if __name__ == "__main__":
    db = DbManagerV1("jp_realestate_v1")
    df1 = db.load_data(include_expired=True)
    cleaner = DataPreprocess()
    df1 = cleaner.run_preprocessor(df1)
    print(df1.info())


