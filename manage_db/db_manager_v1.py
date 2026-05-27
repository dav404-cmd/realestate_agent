import json

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

from sqlalchemy import create_engine
import pandas as pd

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

    @staticmethod
    def get_db_engine():
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")

        engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
        try :
            with engine.connect() as conn:
                pass
        except Exception as e:
            print(f"Connection with engine failed , error : {e}")

        return engine

    def reset_table(self):
        query = sql.SQL("""
        TRUNCATE TABLE {table} RESTART IDENTITY;
        """).format(table = sql.Identifier(self.table_name))
        with self.conn.cursor() as cur:
            cur.execute(query)
            self.conn.commit()
        print(f"Reset {self.table_name}")

    def update_status(self,listing_id:int , status : str):
        query = sql.SQL("""
        UPDATE {table}
        SET status  = %s
        WHERE id = %s; 
        """).format(table = sql.Identifier(self.table_name))
        self.cursor.execute(query,(status,listing_id))
        self.conn.commit()

    def update_last_update(self,listing_id:int):
        query = sql.SQL("""
        UPDATE {table}
        SET last_update = CURRENT_TIMESTAMP
        WHERE id = %s;
        """).format(table = sql.Identifier(self.table_name))
        self.cursor.execute(query,(listing_id,))
        self.conn.commit()

    # QUERYING FUNCTIONS

    def get_active_ids(self):
        query = f"""
        SELECT id,source_listing_id 
        FROM {self.table_name}
        WHERE status = 'active'
        AND last_update < NOW() - INTERVAL '3 days';
        """

        engine = self.get_db_engine()
        df = pd.read_sql(query,engine)

        return df

    def get_by_id(self,id_):
        query = sql.SQL("""
        SELECT *
        FROM {table}
        WHERE id = %s
        """).format(table = sql.Identifier(self.table_name))
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query,(id_,))
            listing = cur.fetchone()

        return listing

    def get_options(self,column_name):
        query = sql.SQL("""
        SELECT DISTINCT data ->> %s AS value 
        FROM {table}
        WHERE data ->> %s IS NOT NULL
        AND data ->> %s != ''
        ORDER BY value 
        """).format(table = sql.Identifier(self.table_name))
        with self.conn.cursor() as cur:
            cur.execute(query,(column_name,column_name,column_name))
            rows = cur.fetchall()
        return rows

    def get_numeric_range(self,column_name):
        query = sql.SQL("""
        SELECT 
        MIN({col}) AS min_value,
        MAX({col}) AS max_value
        FROM {table}
        """).format(
            col = sql.Identifier(column_name),
            table = sql.Identifier(self.table_name)
        )
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur :
            cur.execute(query)
            result = cur.fetchone()

        return result

    def get_json_numeric_range(self, key):
        query = sql.SQL("""
        SELECT
        MIN(NULLIF(data ->> %s, '')::numeric) AS min_value,
        MAX(NULLIF(data ->> %s, '')::numeric) AS max_value
        FROM {table}
        """).format(
            table=sql.Identifier(self.table_name)
        )

        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (key, key))
            result = cur.fetchone()

        return result