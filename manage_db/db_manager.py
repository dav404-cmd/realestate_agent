import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from dotenv import load_dotenv
import os
import json
from sqlalchemy import create_engine
import pandas as pd
from utils.logger import get_logger

from scraper.japan.realestate.clean_data import make_df_structurally_safe

db_log = get_logger("Db_Manager")

load_dotenv()

class DbManager:
    def __init__(self,table_name,source = None):
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

    def delete_all(self):
        db_log.critical(f"This will delete all data from {self.table_name} database")
        do_reset = input(
            "DO YOU WISH TO PROCEED ?\n"
            "TYPE (YES I WANT TO DELETE DATABASE)\n"
            "ANYTHING ELSE WILL BE CONSIDERED NO.\nEnter answer : "
        )

        if do_reset == "YES I WANT TO DELETE DATABASE":
            query = sql.SQL("DELETE FROM {table}").format(table=sql.Identifier(self.table_name))
            self.cursor.execute(query)
            self.conn.commit()
            db_log.critical(f"DELETED all from {self.table_name}")

        else:
            db_log.critical(f"Database {self.table_name} was NOT deleted")



    def fetch_all(self):
        query = sql.SQL("SELECT * FROM {table}").format(table=sql.Identifier(self.table_name))
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @staticmethod
    def get_db_engine():
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT")

        # Replace with your actual credentials
        engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{dbname}")
        try:
            with engine.connect() as conn:
                pass
        except Exception as e:
            print(f"Connection to  {dbname} failed , error : {e}")
        return engine

    @staticmethod
    def auto_cast_numeric(df):
        # Exclude base columns that should not be cast
        exclude = {"id", "source", "scraped_at"}
        for col in df.columns:
            if col not in exclude:
                try:
                    df[col] = pd.to_numeric(df[col])
                except Exception:
                    pass
        return df

    def load_data(self):
        query = f"""
            SELECT id, source, scraped_at, j.key, j.value
            FROM {self.table_name}
            CROSS JOIN LATERAL jsonb_each_text(data) AS j(key, value);
        """
        engine = self.get_db_engine()
        df_long = pd.read_sql(query, engine)

        # Pivot to wide format
        df = df_long.pivot_table(
            index=["id", "source", "scraped_at"],
            columns="key",
            values="value",
            aggfunc="first"
        ).reset_index()

        df = self.auto_cast_numeric(df)

        if self.table_name == "jp_realestate":
            # This table stores heterogeneous scraped JSON
            # Structural normalization is REQUIRED before querying
            df = make_df_structurally_safe(df)

        return df

    def list_tables(self):
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_type = 'BASE TABLE';
        """
        self.cursor.execute(query)
        return [row["table_name"] for row in self.cursor.fetchall()]

