
from manage_db.db_manager import DbManager
from manage_db.db_manager_v1 import DbManagerV1
import re

import json
from psycopg2.extras import RealDictCursor

from data.data_cleaner.to_json_safe import DateTimeEncoder

from scraper.japan.realestate.clean_data import (parse_repair_reserve_fund,
                                                 parse_location,parse_nearest_station)
import ast

class MigrateDb:
    def __init__(self):
        self.db0 = DbManager("jp_realestate")
        self.db1 = DbManagerV1("jp_realestate_v1")

    def load_existing_data(self):
        conn = self.db0.conn
        query = """
        SELECT
            data,
            scraped_at,
            status,
            last_update
        FROM jp_realestate
        WHERE data ->> 'url' IS NOT NULL
        AND data ->> 'price_yen' IS NOT NULL;
        """
        with conn.cursor(cursor_factory = RealDictCursor) as cur:
            cur.execute(query)
            data = cur.fetchall()

        return data

    @staticmethod
    def get_source_listing_id(data):

        url = data.get("url")
        if not url:
            data["source_listing_id"] = None
            return data

        match = re.search(r'/view/(\d+)', url)
        if match:
            data["source_listing_id"] = match.group(1)
        else:
            data["source_listing_id"] = None

        data.pop("url", None)

        return data

    @staticmethod
    def parse_floor(value):
        """
        "floor": [
            21,
            21
        ]
        """

        if not value:
            return {
                "unit_floor": None,
                "total_floors": None
            }

        # Already structured
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return {
                "unit_floor": value[0],
                "total_floors": value[1]
            }

        # If string looks like "[29, 43]" → parse it
        if isinstance(value, str):
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                try:
                    lst = ast.literal_eval(value)
                    if isinstance(lst, (list, tuple)) and len(lst) == 2:
                        return {
                            "unit_floor": int(lst[0]),
                            "total_floors": int(lst[1])}
                except:
                    pass

        return {
            "unit_floor": None,
            "total_floors": None
        }

    @staticmethod
    def parse_floors(value):
        #  "floors": 3
        if not value:
            return {
                "unit_floor": None,
                "total_floors": None
            }

        return {
            "unit_floor": None,
            "total_floors": int(value)
        }

    def transform_data(self,payload : dict):
        transform  = {
            "floor" : self.parse_floor,
            "floors": self.parse_floors,
            "location" : parse_location,
            "nearest_station" : parse_nearest_station,
            "repair_reserve_fund" : parse_repair_reserve_fund,
        }
        final = {}

        for clean_key,clean_value in payload.items():
            if clean_key in transform:

                clean_value = transform[clean_key](clean_value)

                if isinstance(clean_value,dict):
                    final.update(clean_value)
                    continue

            final[clean_key] = clean_value

        return final

    def clean_existing_data(self):
        rows = self.load_existing_data()
        cleaned_data = []

        for row in rows:
            payload = self.get_source_listing_id(dict(row["data"]))

            clean_payload = self.transform_data(payload)

            cleaned_data.append({
            "scraped_at": row["scraped_at"],
            "status": row["status"],
            "last_update": row["last_update"],
            "data": clean_payload
            })


        return cleaned_data


    def store_existing_data(self):
        # Will start for id : 33
        data = self.clean_existing_data()
        query = """
                INSERT INTO jp_realestate_v1 (scraped_at,status,last_update,price_yen,source_listing_id,source,data)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (source,source_listing_id) DO NOTHING
                RETURNING id;
                """

        index = 1
        ids = []
        conn = self.db1.conn

        with conn.cursor() as cur:
            for row in data:
                clean_payload = dict(row["data"])
                price_yen = clean_payload.pop("price_yen", None)
                source_listing_id = clean_payload.pop("source_listing_id",None)
                cur.execute(query, [
                    row["scraped_at"],
                    row["status"],
                    row["last_update"],
                    price_yen,
                    source_listing_id,
                    "realestate.co",
                    json.dumps(clean_payload, ensure_ascii=False)
                ])

                result = cur.fetchone()
                if result:
                    ids.append(result[0])
                index += 1
                if index % 1000 == 0:
                    print(f"stored {index} listing ")

        conn.commit()
        conn.close()
        return ids


    def test_data(self):

        conn = self.db1.conn

        query = "SELECT * FROM jp_realestate_v1 WHERE id <= 33;"

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            result = cur.fetchall()
        json_data = json.dumps(result, cls=DateTimeEncoder)
        print(json_data)

if __name__ == "__main__":
    mdb = MigrateDb()
    mdb.test_data()
