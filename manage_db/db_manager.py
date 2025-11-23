import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from dotenv import load_dotenv
import os
import json

from utils.logger import get_logger

db_log = get_logger("Db_Manager")

load_dotenv()

class DbManager:
    def __init__(self,table_name,source):
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
        self.cursor.close()
        self.conn.close()

    def create_table(self):
        query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {table} (
                id SERIAL PRIMARY KEY,
                source TEXT,
                scraped_at TIMESTAMP DEFAULT NOW(),
                data JSONB
            );
        """).format(table=sql.Identifier(self.table_name))
        self.cursor.execute(query)
        self.conn.commit()
        db_log.info(f"created table : {self.table_name}")

    def insert_listing(self, listings):
        query = sql.SQL("""
            INSERT INTO {table} (source, data)
            VALUES (%s, %s)
            ON CONFLICT ((data->>'url')) DO NOTHING
            RETURNING id;
        """).format(table=sql.Identifier(self.table_name))

        ids = []
        with self.conn.cursor() as cur:
            for listing in listings:
                cur.execute(query, [
                    self.source,
                    json.dumps(listing, ensure_ascii=False),
                ])
                result = cur.fetchone()
                if result:  # only append if insert succeeded
                    ids.append(result[0])
            self.conn.commit()

        return ids

    def fetch_all(self):
        query = sql.SQL("SELECT * FROM {table}").format(table=sql.Identifier(self.table_name))
        self.cursor.execute(query)
        return self.cursor.fetchall()

