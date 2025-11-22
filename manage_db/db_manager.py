import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from dotenv import load_dotenv
import os
import json

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
        print(f"created table : {self.table_name}")

    def insert_listing(self,final):
        query = sql.SQL("""
            INSERT INTO {table} (source, data)
            VALUES (%s, %s)
            RETURNING id;
        """).format(table=sql.Identifier(self.table_name))
        with self.conn.cursor() as cur:
            cur.execute(query, [
                self.source,
                json.dumps(final, ensure_ascii=False),
            ])
            self.conn.commit()
            return cur.fetchone()[0]

    def fetch_all(self):
        query = sql.SQL("SELECT * FROM {table}").format(table=sql.Identifier(self.table_name))
        self.cursor.execute(query)
        return self.cursor.fetchall()


if __name__ == "__main__":
    db = DbManager("test","example")
    db.create_table()
    new_id = db.insert_listing({
    "price_yen": 133800000,
    "building_name": "🔸S091 SHIMOKITAZAWA 3LDK HOUSE🔸",
    "floors": "2F",
    "available_from": "May 28, 2025",
    "type": "House",
    "size": 104.33,
    "land_area": 89.61,
    "land_rights": "Freehold",
    "location": "Daita, Setagaya-ku, Tokyo",
    "occupancy": "Vacant",
    "nearest_station": "Setagaya Daita Station (8 min. walk) Odakyū Line",
    "layout": "2LDK",
    "construction_completed": 2025,
    "direction_facing": "West",
    "transaction_type": "Brokerage",
    "floor_area_ratio": 200.0,
    "building_area_ratio": 80.0,
    "zoning": "Residential",
    "road_width": 4,
    "structure": "Wood",
    "building_description": "Looking for an English-speaking real estate broker in Tokyo? Whether you're overseas or in Tokyo, I provide professional, accurate advice as a licensed real estate broker specializing in luxury homes across the Tokyo Metropolitan area. I work with both international and local buyers and sellers, ensuring a seamless experience. With bilingual and bicultural expertise, including experience as an agent in New York, I understand the needs of clients from diverse backgrounds. All communication and assistance are in English, making the process smooth and stress-free. For reliable guidance and exceptional service, feel free to contact me anytime to get started. 🔹Licensed Real Estate Broker🔹 Aki Shimizu, RE/MAX Top Agent 090-4677-7502 aki@topagent-tokyo.com Find out who I am more on topagent-tokyo.com",
    "other_expenses": 5,
    "landmarks": "・Honda Gekijō Theater ・Shimokitazawa Shelter (live music venue) ・Village Vanguard Shimokitazawa",
    "parking": "Available",
    "date_updated": "Oct 23, 2025",
    "next_update_schedule": "Nov 22, 2025",
    "url": "https://realestate.co.jp/en/forsale/view/1230859",
    "source": "realestate.io"
  })
    print("Inserted row id:", new_id)
    rows = db.fetch_all()
    print(rows)
    db.close_conn()