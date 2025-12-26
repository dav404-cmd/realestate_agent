from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import pandas as pd

from manage_db.db_manager import DbManager
from manage_db.query import query_properties, PropertyQuery

from data.data_cleaner.to_json_safe import df_to_json_safe_records

from utils.logger import get_logger
api_log = get_logger("API_log")

app = FastAPI()
df : pd.DataFrame | None = None

@app.on_event("startup")
def load_data():
    global df
    db = DbManager(table_name="jp_realestate")
    df = db.load_data()
    db.close_conn()
    api_log.info(f"Loaded {len(df)} rows into memory")

@app.post("/search")
def search(q: PropertyQuery):
    api_log.info(f"Received query: {q}")
    try:
        if df is None:
            return {"error":"Data not loaded"}
        results = query_properties(df,q)
        return jsonable_encoder(df_to_json_safe_records(results))
    except Exception as e:
        api_log.exception("Search failed")
        return {"error": str(e)}


if __name__ == "__main__":
    #__test__
    db = DbManager(table_name="jp_realestate")
    df = db.load_data()
    db.close_conn()

    q = PropertyQuery(
        max_price=400000000,
        min_size=40,
        limit=2
    )
    results = query_properties(df, q)
    df_2 = jsonable_encoder(df_to_json_safe_records(results))

    print(JSONResponse(content=df_2).body)
