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
        df = df.drop(columns = ["gross_yield","floor_area_ratio","building_area_ratio",
                                "balcony_size","land_area","potential_annual_rent","investment_situation"])
        return df

    @staticmethod
    def split_location(df) -> pd.DataFrame:
        df["location"] = df["location"].fillna("")
        parts = df["location"].str.split(",",expand = True)
        df["prefecture"] = parts[2].str.strip()
        df = df.drop(columns=["location"])
        return df

    @staticmethod
    def clean_onehot_encoding(df) -> pd.DataFrame:
        df = df.join(pd.get_dummies(df["prefecture"], prefix="prefecture").astype(int)).drop("prefecture", axis=1)
        df = df.join(pd.get_dummies(df["land_rights"], prefix="land_rights").astype(int)).drop("land_rights", axis=1)
        df = df.join(pd.get_dummies(df["occupancy"], prefix="occ").astype(int)).drop("occupancy", axis=1)
        df = df.join(pd.get_dummies(df["structure"], prefix="structure").astype(int)).drop("structure", axis=1)
        df = df.join(pd.get_dummies(df["zoning"], prefix="zoning").astype(int)).drop("zoning", axis=1)
        df = df.join(pd.get_dummies(df["transaction_type"], prefix="transaction").astype(int)).drop("transaction_type",axis=1)
        df = df.join(pd.get_dummies(df["type"], prefix="type").astype(int)).drop("type", axis=1)
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

        # 4. Studio / R-type detection (1R, R, SR)
        r_pattern = r"(^1R$)|(^R$)|(^SR$)|(\b1R\b)|(\bR\b)"
        is_r_type = df["layout"].str.contains(r_pattern, case=False)

        # 5. Fill missing rooms for whole buildings with NaN (can't infer)
        df.loc[df["is_whole_building"] == 1, "rooms"] = np.nan

        df = df.drop(columns=["layout"])

        return df

    @staticmethod
    def clean_direction(df) -> pd.DataFrame:
        valid_dirs = {
            "NORTH", "SOUTH", "EAST", "WEST",
            "NORTHEAST", "NORTHWEST",
            "SOUTHEAST", "SOUTHWEST"
        }
        def get_valid_dirs(d):
            if pd.isna(d):
                return []
            parts = [p.strip().upper() for p in d.split(",")]
            return [p for p in parts if p in valid_dirs]

        df["direction_list"] = df["direction_facing"].apply(get_valid_dirs)

        for d in valid_dirs:
            df[f"dir_{d}"] = df["direction_list"].apply(lambda lst: int(d in lst))

        df = df.drop(columns = ["direction_facing","direction_list"])

        return df

    @staticmethod
    def clean_repair_reserve(df) -> pd.DataFrame:
        df["repair_reserve_fund"] = (
            df["repair_reserve_fund"].
            fillna("").astype(str).str
            .replace(r"/D","",regex = True).replace("",None)
            .pipe(pd.to_numeric,errors = "coerce")
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
                return pd.Series([None, None, None, None])

            # Regex to capture: Station name, minutes, mode, line
            match = re.match(r"^(.*?) Station \((\d+) min\. (.*?)\) (.*)$", s)
            if match:
                station_name = match.group(1).strip()
                minutes = int(match.group(2))
                mode = match.group(3).strip()
                line = match.group(4).strip()
                return pd.Series([station_name, minutes, mode, line])
            else:
                return pd.Series([s, None, None, None])  # fallback

        df[['ns_station_name', 'ns_minutes', 'ns_mode', 'ns_line']] = df['nearest_station'].apply(parse_station)

        # Top 10 stations
        top10_stations = df['ns_station_name'].value_counts().nlargest(10).index
        df['ns_station_name_reduced'] = df['ns_station_name'].where(df['ns_station_name'].isin(top10_stations), 'Other')

        # Top 10 lines
        top10_lines = df['ns_line'].value_counts().nlargest(10).index
        df['ns_line_reduced'] = df['ns_line'].where(df['ns_line'].isin(top10_lines), 'Other')

        df = df.drop(columns=['nearest_station','ns_station_name','ns_minutes','ns_mode','ns_line'])

        return df

    @staticmethod
    def format_columns(df):
        df.columns = df.columns.str.replace(" ", "_")
        return df

    def run_preprocessor(self,df):
        df = self.drop_unnecessary(df)
        df = self.drop_difficult(df)
        df = self.split_location(df)
        df = self.clean_onehot_encoding(df)
        df = self.clean_dates(df)
        df = self.clean_layout(df)
        df = self.clean_direction(df)
        df = self.clean_ns_station(df)
        df = self.format_columns(df)

        return df


if __name__ == "__main__":
    db = DbManager("jp_realestate")
    df1 = db.load_data()
    cleaner = DataPreprocess()
    df1 = cleaner.run_preprocessor(df1)
    print(df1.info())


