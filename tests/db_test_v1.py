import json
from pathlib import Path
from fastapi.responses import JSONResponse
from data.data_cleaner.to_json_safe import DateTimeEncoder
from manage_db.db_manager_v1 import DbManagerV1

from psycopg2.extras import RealDictCursor

def test_json_1():
    root = Path(__file__).parents[1].resolve()

    json_path = root / "data" / "raw" / "real_estate.json"

    with open(json_path,'r',encoding="utf-8-sig") as f:
        loaded_data = json.load(f)


    print(JSONResponse(loaded_data).body)

def test_json_2():
    db = DbManagerV1(None,None)
    conn = db.conn

    query = "SELECT * FROM jp_realestate_v1;"

    with conn.cursor(cursor_factory=RealDictCursor) as cur :
        cur.execute(query)
        result = cur.fetchall()
    conn.commit()
    conn.close()
    json_data = json.dumps(result,cls=DateTimeEncoder)
    print(json_data)

if __name__ == "__main__":
    test_json_2()