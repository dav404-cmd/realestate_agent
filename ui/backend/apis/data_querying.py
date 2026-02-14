from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from manage_db.db_manager import DbManager
from manage_db.query import query_properties, PropertyQuery

from data.data_cleaner.to_json_safe import df_to_json_safe_records

from utils.logger import get_logger

api_log = get_logger("API_log")

@asynccontextmanager
async def lifespan(app:FastAPI):
    db = DbManager(table_name="jp_realestate")
    df = db.load_data()
    db.close_conn()

    app.state.df = df
    api_log.info(f"Loaded {len(df)} rows into memory")

    yield

    api_log.info("Application shutdown complete")


app = FastAPI(lifespan=lifespan)


@app.post("/search")
def search(q: PropertyQuery):
    api_log.info(f"Received query: {q}")
    try:
        if app.state.df is None:
            return {"error":"Data not loaded"}
        results = query_properties(app.state.df,q)
        return jsonable_encoder(df_to_json_safe_records(results))
    except Exception as e:
        api_log.exception("Search failed")
        return {"error": str(e)}

@app.get("/property/{property_id}")
def get_property(property_id:int):
    api_log.info(f"Received request for id : {property_id}")
    try:
        if app.state.df is None:
            return {"error":"Data not loaded"}

        property_data = app.state.df[app.state.df['id'] == property_id]
        if property_data.empty:
            return {"error": "property not found"}

        # Take the first row, convert to dict, then sanitize
        safe_record = df_to_json_safe_records(property_data.iloc[[0]])[0]
        return jsonable_encoder(safe_record)


    except Exception as e:
        api_log.exception("Get property failed")
        return {"error": str(e)}

@app.get("/options/{column_name}")
def get_options(column_name:str):
    api_log.info(f"Received options request for column : {column_name}")
    try:
        if app.state.df is None:
            return {"error":"Data not loaded"}

        options = app.state.df[column_name].unique().tolist()

        return {column_name:options}

    except Exception as e:
        api_log.exception("Get options failed")
        return {"error":str(e)}

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
