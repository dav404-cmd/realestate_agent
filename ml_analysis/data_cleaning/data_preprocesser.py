import pandas as pd
import numpy as np
import re
from datetime import datetime

from manage_db.db_manager import DbManager

pd.set_option("display.max_columns", None)

class DataPreprocess:
    @staticmethod
    def drop_unnecessary(df) -> pd.DataFrame:
        df = df.drop(columns=["id","source","scraped_at","building_description","building_name","date_updated",
                                        "unit_number","unit_summary","url","next_update_schedule","landmarks",
                                        "manager_style","manage_type","other_expenses","sell_situation","road_width"])
        return df

    @staticmethod
    def drop_difficult(df) -> pd.DataFrame:
        # Useful data currently unusable due to high non value.
        df = df.drop(columns = ["potential_annual_rent","investment_situation"])
        return df

    SPARSE_NUMERIC = [
        "gross_yield",
        "floor_area_ratio",
        "building_area_ratio",
        "balcony_size",
        "land_area"
    ]

    @staticmethod
    def handle_sparse_numeric(df):
        for col in DataPreprocess.SPARSE_NUMERIC:
            if col in df.columns:
                df[f"{col}_missing"] = df[col].isna().astype(int)
        return df

    @staticmethod
    def split_location(df) -> pd.DataFrame:
        df["location"] = df["location"].fillna("")
        parts = df["location"].str.split(",",expand = True)
        df["prefecture"] = parts[2].str.strip()
        df = df.drop(columns=["location"])
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
        def parse_dirs(s):
            if pd.isna(s):
                return []
            parts = [p.strip().upper() for p in s.split(",")]
            return [p for p in parts if p in DataPreprocess.DIR_ANGLE]

        df["dir_list"] = df["direction_facing"].apply(parse_dirs)

        df["num_directions"] = df["dir_list"].apply(len)

        def avg_angle(dirs):
            if not dirs:
                return np.nan
            return np.mean([DataPreprocess.DIR_ANGLE[d] for d in dirs])

        df["avg_direction_angle"] = df["dir_list"].apply(avg_angle)

        df["has_south_exposure"] = df["dir_list"].apply(
            lambda d: int(any(x in ["SOUTH", "SOUTHEAST", "SOUTHWEST"] for x in d))
        )

        return df.drop(columns=["direction_facing", "dir_list"])

    @staticmethod
    def clean_repair_reserve(df) -> pd.DataFrame:
        df["repair_reserve_fund"] = (
            df["repair_reserve_fund"]
            .astype(str)
            .str.replace(r"\D", "", regex=True)
            .replace("", pd.NA)
        )

        df["repair_reserve_fund"] = pd.to_numeric(
            df["repair_reserve_fund"], errors="coerce"
        )

        df["repair_reserve_fund_missing"] = (
            df["repair_reserve_fund"].isna().astype("int8")
        )

        return df
    @staticmethod
    def clean_dates(df) -> pd.DataFrame:
        current_year = datetime.now().year

        df['built_year'] = df["construction_completed"].fillna(df["year_built"])

        df['built_year'] = df['built_year'].astype('Int64')
        df['building_age'] = current_year - df['built_year']

        # Convert to datetime
        df['available_from'] = pd.to_datetime(df['available_from'], errors='coerce')

        # Create a missing flag
        df['available_from_missing'] = df['available_from'].isna().astype(int)

        # Days until available (NaN stays if missing)
        df['days_until_available'] = (df['available_from'] - pd.Timestamp.today()).dt.days

        # Extract month and year for seasonality patterns
        df['available_month'] = df['available_from'].dt.month
        df['available_year'] = df['available_from'].dt.year

        df = df.drop(columns=["available_from","construction_completed","year_built"])

        return df

    @staticmethod
    def clean_ns_station(df):
        def parse_station(s):
            if pd.isna(s):
                return pd.Series([None, None])

            match = re.match(r"^(.*?) Station \((\d+) min", s)
            if match:
                return pd.Series([match.group(1), int(match.group(2))])
            return pd.Series([s, None])

        df[["ns_station_name", "ns_minutes"]] = df["nearest_station"].apply(parse_station)

        df["ns_minutes_missing"] = df["ns_minutes"].isna().astype(int)

        top10_stations = df["ns_station_name"].value_counts().nlargest(10).index
        df["ns_station_name"] = df["ns_station_name"].where(df["ns_station_name"].isin(top10_stations),"Other")

        return df.drop(columns=["nearest_station"])


    @staticmethod
    def format_columns(df):
        df.columns = df.columns.str.replace(" ", "_")
        return df


    PIPELINE = [
        drop_unnecessary,
        drop_difficult,
        handle_sparse_numeric,
        split_location,
        clean_repair_reserve,
        clean_dates,
        clean_layout,
        clean_direction,
        clean_ns_station,
        format_columns
    ]
    def run_preprocessor(self,df):
        for step in self.PIPELINE:
            df = step(df)
        return df


if __name__ == "__main__":
    db = DbManager("jp_realestate")
    df1 = db.load_data()
    cleaner = DataPreprocess()
    df1 = cleaner.run_preprocessor(df1)
    print(df1.info())


