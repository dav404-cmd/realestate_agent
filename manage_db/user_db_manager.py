import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

from dotenv import load_dotenv
import os

load_dotenv()

class UserDbManager:
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

    def create_table_user(self):

        query = """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email TEXT UNIQUE NOT NULL,
            google_sub TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
    );
        """

        self.cursor.execute(query)
        self.conn.commit()

    def create_table_user_pref(self):
        pass

    def insert_user(self,email,google_sub):
        query = """
        INSERT INTO users (email,google_sub)
        VALUES (%s,%s)
        ON CONFLICT (google_sub)
        DO UPDATE SET email = EXCLUDED.email
        RETURNING id;
        """
        self.cursor.execute(query,(email,google_sub))
        user_id = self.cursor.fetchone()["id"]
        self.conn.commit()
        if user_id:
            return user_id
        return None


