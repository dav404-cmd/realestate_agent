import pandas as pd
from pydantic import BaseModel
from typing import Optional, List

from manage_db.db_manager import DbManager

def build_db_profile(df:pd.DataFrame):
    profile = {}
    ignore = ["url","building_description"]
    for col in df.columns:
        if col in ignore:
            continue

        series = df[col].dropna()

        if series.empty:
            continue

        if pd.api.types.is_numeric_dtype(series):
            profile[col] = {
                "type":"numeric",
                "min" : float(series.min()),
                "max" : float(series.max()),
                "avg" : float(series.mean())
            }
        else:
            profile[col] = {
                "type" : "categorical",
                "unique_samples" : list(series.unique()[:20])
            }
    return profile

class PropertyQuery(BaseModel):
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_size: Optional[float] = None
    max_size: Optional[float] = None
    zoning: Optional[str] = None
    structure: Optional[str] = None
    occupancy: Optional[str] = None
    nearest_station: Optional[str] = None
    limit: int = 20
    sort_by: str = "price_yen"
    sort_order: str = "asc"

def query_properties(df: pd.DataFrame, q: PropertyQuery) -> pd.DataFrame:
    result = df.copy()

    if q.min_price is not None:
        result = result[result["price_yen"] >= q.min_price]

    if q.max_price is not None:
        result = result[result["price_yen"] <= q.max_price]

    if q.min_size is not None:
        result = result[result["size"] >= q.min_size]

    if q.max_size is not None:
        result = result[result["size"] <= q.max_size]

    if q.zoning:
        result = result[result["zoning"].str.contains(q.zoning, case=False, na=False)]

    if q.structure:
        result = result[result["structure"].str.contains(q.structure, case=False, na=False)]

    if q.occupancy:
        result = result[result["occupancy"].str.contains(q.occupancy, case=False, na=False)]

    if q.nearest_station:
        result = result[result["nearest_station"].str.contains(q.nearest_station, case=False, na=False)]

    ascending = q.sort_order == "asc"
    result = result.sort_values(q.sort_by, ascending=ascending)

    return result.head(q.limit)

if __name__ == "__main__":
    db = DbManager(table_name="jp_realestate")
    df = db.load_data()

    q = PropertyQuery(
        max_price=400_000_000,
        min_size=80,
        zoning="Residential",
        nearest_station="Hiroo"
    )

    results = query_properties(df, q)

    print(results[[
        "price_yen",
        "size",
        "nearest_station",
        "zoning",
        "structure",
        "url"
    ]])

    profile = build_db_profile(df)
    print(profile)
