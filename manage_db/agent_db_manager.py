import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extras import Json

from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

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

    def create_indexes(self):
        thread_id_index = """
        CREATE INDEX IF NOT EXISTS idx_agent_message_thread
        ON agent_message(thread_id);
        """
        self.cursor.execute(thread_id_index)
        self.conn.commit()

    def new_thread(self,user_id,title):
        query = """
        INSERT INTO agent_thread (user_id,title)
        VALUES (%s,%s)
        RETURNING id;
        """
        self.cursor.execute(query,(user_id,title))
        self.conn.commit()
        row = self.cursor.fetchone()
        if row:
            agent_log.info(f"New thread made : {row['id']}")
            return row["id"]
        agent_log.warning("Insert failed could be due to id dups")
        return None

    def insert_message(self,thread_id,reduced_state):
        query = """
        INSERT INTO agent_message (thread_id,user_input,response,intent,extracted_filters,result_ids)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING id;
        """
        self.cursor.execute(query, (
            thread_id,
            reduced_state.get('user_input'),
            reduced_state.get('response'),
            reduced_state.get('intent'),
            Json(reduced_state.get('extracted_filters')),
            Json(reduced_state.get('result_ids')),
        ))
        self.conn.commit()
        row = self.cursor.fetchone()
        if row:
            agent_log.info(f"message stored for : {row['id']}")
            return row["id"]
        agent_log.warning("Insert failed .")
        return None

    def get_messages(self,thread_id):
        query = """
        SELECT user_input,response,created_at
        FROM agent_message 
        WHERE thread_id = %s;
        """
        self.cursor.execute(query,(thread_id,))
        rows = self.cursor.fetchall()
        if rows:
            agent_log.info(f"Got messages for : {thread_id}")
            return rows
        agent_log.warning(f"Rows not found for {thread_id}")
        return []

    def get_threads(self,user_id):
        query = """
        SELECT id,title,created_at,updated_at
        FROM agent_thread
        WHERE user_id = %s;
        """
        self.cursor.execute(query,(user_id,))
        rows = self.cursor.fetchall()
        if rows:
            agent_log.info(f"Got threads for user : {user_id}")
            return rows
        agent_log.warning(f"Threads not found for user : {user_id}")
        return []

if __name__ == "__main__":
    db = AgentMemory()
    results = db.get_threads(os.getenv("TEST_USER_ID"))
    json_data = jsonable_encoder(results)
    print(JSONResponse(content=json_data).body)
    db.close_conn()