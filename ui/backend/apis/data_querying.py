from fastapi import FastAPI
from fastapi import APIRouter
from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from manage_db.db_manager_v1 import DbManagerV1
from manage_db.query import PropertyQuery ,query_property

from utils.logger import get_logger

router = APIRouter()
api_log = get_logger("API_log")

@asynccontextmanager
async def lifespan(app:FastAPI):
    db = DbManagerV1(table_name="jp_realestate_v1")

    app.state.db = db

    api_log.info(f"Database connected . Application started.")

    yield

    db.close_conn()
    api_log.info("Application shutdown complete")


@router.post("/search")
def search(q: PropertyQuery,request : Request):
    api_log.info(f"Received query: {q}")
    try:
        results = query_property(q,"jp_realestate_v1",request.app.state.db.conn)
        return jsonable_encoder(results)
    except Exception as e:
        api_log.exception("Search failed")
        return {"error": str(e)} #todo : switch to http errors

@router.get("/property/{property_id}")
def get_property(property_id:int,request : Request):
    api_log.info(f"Received request for id : {property_id}")
    try:
        property_data = request.app.state.db.get_by_id(property_id)
        if not property_data:
            return {"error": "property not found"}

        # Take the first row, convert to dict, then sanitize
        safe_record = property_data
        return jsonable_encoder(safe_record)


    except Exception as e:
        api_log.exception("Get property failed")
        return {"error": str(e)}

@router.get("/options/{column_name}")
def get_options(column_name:str,request : Request):
    api_log.info(f"Received options request for column : {column_name}")
    try:
        rows = request.app.state.db.get_options(column_name)
        options = [row[0] for row in rows if row[0]]

        return {
            "column_name":column_name,
            "options":options
        }

    except Exception as e:
        api_log.exception("Get options failed")
        return {"error":str(e)}

if __name__ == "__main__":
    #__test__
    db = DbManagerV1(table_name="jp_realestate_v1")
    conn = db.conn

    q = PropertyQuery(
        max_price=400000000,
        min_size=40,
        limit=2
    )
    results = query_property(q , "jp_realestate_v1" , conn)
    data = jsonable_encoder(results)

    print(JSONResponse(content=data).body)
