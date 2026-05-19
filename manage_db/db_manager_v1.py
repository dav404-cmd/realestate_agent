import json

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

from dotenv import load_dotenv
import os

load_dotenv()
#jp_realestate_v1
class DbManagerV1:
    def __init__(self,table_name :str | None , source = str | None):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        self.table_name = table_name
        self.source = source

    def close_conn(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_table(self):
        query = sql.SQL("""
        CREATE TABLE IF NOT EXISTS {table} (
        id SERIAL PRIMARY KEY,
        source TEXT NOT NULL,
        scraped_at TIMESTAMPTZ DEFAULT NOW(),
        data JSONB,
        status TEXT DEFAULT 'active',
        last_update TIMESTAMPTZ DEFAULT NOW(),
        price_yen BIGINT,
        source_listing_id TEXT NOT NULL 
        )
        """).format(table = sql.Identifier(self.table_name))

        index_query = sql.SQL("""
        CREATE UNIQUE INDEX IF NOT EXISTS {index_name}
        ON {table} (source,source_listing_id);
        """).format(
            index_name = sql.Identifier(f"listing_unique_idx_{self.table_name}"),
            table = sql.Identifier(self.table_name)
                    )

        partial_idx_query = sql.SQL("""
        CREATE INDEX IF NOT EXISTS {index_name}
        ON {table} (price_yen)
        WHERE status = 'active';
        """).format(
            index_name = sql.Identifier(f"idx_active_listing_{self.table_name}"),
            table = sql.Identifier(self.table_name))

        with self.conn.cursor() as cur:

            cur.execute(query)
            cur.execute(index_query)
            cur.execute(partial_idx_query)

        self.conn.commit()
        print(f"Table {self.table_name} has been created.")

    def insert_data(self,listings): # Stores the data of a page at once
        query = sql.SQL("""
        INSERT INTO {table} (price_yen,source_listing_id,source,data)
        VALUES (%s,%s,%s,%s)
        ON CONFLICT (source,source_listing_id) DO NOTHING
        RETURNING id;
        """).format(table = sql.Identifier(self.table_name))

        ids = []
        with self.conn.cursor() as cur:
            for listing in listings:
                clean_payload = dict(listing)
                price_yen = clean_payload.pop('price_yen',None)
                source_listing_id = clean_payload.pop('source_listing_id',None)

                cur.execute(query,[
                    price_yen,source_listing_id,self.source,
                    json.dumps(clean_payload,ensure_ascii=False)
                ])
                result = cur.fetchone()
                if result:
                    ids.append(result[0])
            self.conn.commit()
        return ids

    def delete_all(self):
        query = sql.SQL("""
        DELETE FROM {table};
        """).format(table = sql.Identifier(self.table_name))
        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()
        print(f"deleted all data form {self.table_name}")
