import psycopg2
from psycopg2.extras import RealDictCursor

import os
from dotenv import load_dotenv
from utils.logger import get_logger

agent_log = get_logger("AgentMemory")

load_dotenv()

class AgentMemory:
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

    def create_thread_table(self):
        extension_query = """
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        """
        query = """
        CREATE TABLE IF NOT EXISTS agent_thread (
        
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL,
        
        title TEXT NOT NULL,
        
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        
        CONSTRAINT fk_user_thread_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        )
        """
        self.cursor.execute(extension_query)
        self.cursor.execute(query)
        self.conn.commit()
        agent_log.info("Created agent_thread table")

    def create_agent_messages_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS agent_message (
        
        id SERIAL PRIMARY KEY,
        thread_id UUID NOT NULL,
        
        user_input TEXT,
        intent TEXT,
        
        extracted_filters JSONB,
        result_ids JSONB,
        
        response TEXT, 
        
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        
        CONSTRAINT fk_id_thread_id
        FOREIGN KEY (thread_id)
        REFERENCES agent_thread(id)
        ON DELETE CASCADE
        )
        """
        self.cursor.execute(query)
        self.conn.commit()
        agent_log.info("Created agent_message table")


if __name__ == "__main__":
    db = AgentMemory()
    db.create_agent_messages_table()
    db.close_conn()