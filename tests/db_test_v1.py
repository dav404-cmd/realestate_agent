import json
from pathlib import Path
from fastapi.responses import JSONResponse
from data.data_cleaner.to_json_safe import DateTimeEncoder
from manage_db.db_manager_v1 import DbManagerV1

from psycopg2.extras import RealDictCursor
import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration

@pytest.fixture
def db():
    db_logic = DbManagerV1("jp_realestate_v1")
    yield db_logic
    db_logic.close_conn()

def test_conn(db):
    assert db.conn is not None
    assert db.cursor is not None

def test_engine_connectivity(db):
    engine = db.get_db_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

# data quality test
def test_json_1():
    # value returned from scraper .
    root = Path(__file__).parents[1].resolve()

    json_path = root / "data" / "raw" / "real_estate.json"

    with open(json_path,'r',encoding="utf-8-sig") as f:
        loaded_data = json.load(f)

    response = JSONResponse(loaded_data)

    assert response.body is not None
    assert len(response.body) > 0

def test_json_2():
    db = DbManagerV1(None,None)
    conn = db.conn

    query = "SELECT * FROM jp_realestate_v1 LIMIT 10;"

    with conn.cursor(cursor_factory=RealDictCursor) as cur :
        cur.execute(query)
        result = cur.fetchall()
    json_data = json.dumps(result,cls=DateTimeEncoder)
    assert json_data is not None
    assert len(json_data) > 0

# check for bad data
def test_bad_data(db):
    uncleaned = db.get_broken_data()
    uncleaned_count = uncleaned["count"]

    query = """
    SELECT COUNT(*)
        FROM jp_realestate_v1
        WHERE price_yen IS NULL 
    """

    db.cursor.execute(query)
    price_null_count = db.cursor.fetchone()['count']

    assert int(uncleaned_count) == 0 , f"Uncleaned data is present in db , count : {uncleaned_count}"
    assert int(price_null_count) == 0 , f"Listing with price null present in db , count : {price_null_count}"