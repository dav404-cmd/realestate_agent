import psycopg2
from psycopg2.extras import RealDictCursor

from dotenv import load_dotenv
import os

load_dotenv()

class ImageDb:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def close_conn(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS jp_realestate_image (

            id SERIAL PRIMARY KEY,
            listing_id INT NOT NULL,

            image_url TEXT NOT NULL,
            image_order SMALLINT NOT NULL,

            created_at TIMESTAMPTZ DEFAULT NOW(),

            CONSTRAINT fk_image_listing_id
                FOREIGN KEY (listing_id)
                REFERENCES jp_realestate_v1(id)
                ON DELETE CASCADE
        );
        """

        unique_index = """
        CREATE UNIQUE INDEX IF NOT EXISTS image_index_jp
        ON jp_realestate_image (listing_id, image_order);
        """

        with self.conn.cursor() as cur:
            cur.execute(query)
            cur.execute(unique_index)

        self.conn.commit()

    def insert_ima_url(self,listing_id,urls_pack):
        _id = []
        for order,url in enumerate(urls_pack):
            query = """
            INSERT INTO jp_realestate_image (listing_id,image_order,image_url)
            VALUES (%s,%s,%s)
            ON CONFLICT (listing_id, image_order) 
            DO NOTHING
            RETURNING id;
            """
            self.cursor.execute(query,(listing_id,order,url))
            row = self.cursor.fetchone()
            if row:
                _id.append(row["id"])
        self.conn.commit()
        return _id

    def remap(self):
        add_query = """
        ALTER TABLE jp_realestate_image
        ADD COLUMN image_url TEXT;
        """
        drop_query = """
        ALTER TABLE jp_realestate_image
        DROP COLUMN storage_path;
        """
        change_col_query = """
        ALTER TABLE jp_realestate_image 
        ALTER COLUMN image_order TYPE SMALLINT;
        """
        with self.conn.cursor() as cur:
            cur.execute(add_query)
            cur.execute(drop_query)
            cur.execute(change_col_query)

        self.conn.commit()

    def reset(self):
        query = """
        TRUNCATE TABLE jp_realestate_image RESTART IDENTITY;
        """
        self.cursor.execute(query)
        self.conn.commit()

    def has_image(self,listing_id) -> bool:
        query = """
        SELECT EXISTS(
            SELECT 1 
            FROM jp_realestate_image
            WHERE listing_id = %s
        );
        """
        self.cursor.execute(query,(listing_id,))
        return self.cursor.fetchone()[0]

    def get_listing_ids_with_images(self) -> set[int]:
        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT DISTINCT listing_id
            FROM jp_realestate_image
            """)
            return {row[0] for row in cur.fetchall()}

if __name__ == "__main__":
    db = ImageDb()
    db.create_table()
    db.close_conn()