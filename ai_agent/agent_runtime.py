from ai_agent.agent_graph import build_graph
from ai_agent.llm_wrappers import OpenRouterLLM

import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver

from manage_db.agent_db_manager import AgentMemory

import os
from dotenv import load_dotenv

load_dotenv()

from utils.logger import get_logger

llm_log = get_logger("RunTime")

class MultiLLm:
    def __init__(self,models):
        self.models = models

    def invoke(self,**kwargs):
        last_error = None

        for i,model in enumerate(self.models):
            try:
                llm_log.info(f" current model : {model.model}")
                return model.invoke(**kwargs)
            except Exception as e:
                llm_log.warning(
                    f"{model.__class__.__name__} failed."
                    f"Trying fallback ({i + 1}/{len(self.models)}). Error: {e}"
                )
                last_error = e
        raise last_error



class AgentRuntime:
    _conn = None
    _graph = None
    _llm = None
    _checkpointer = None
    _db = None

    def __init__(self, conn):

        if AgentRuntime._checkpointer is None:
            db_url = (
                f"postgresql://"
                f"{os.getenv('DB_USER')}:"
                f"{os.getenv('DB_PASSWORD')}@"
                f"{os.getenv('DB_HOST')}:"
                f"{os.getenv('DB_PORT')}/"
                f"{os.getenv('DB_NAME')}"
            )

            checkpoint_conn = psycopg.connect(
                db_url,
                autocommit=True,
                prepare_threshold=None,
                row_factory=dict_row,
            )
            AgentRuntime._checkpointer = PostgresSaver(checkpoint_conn)
            AgentRuntime._checkpointer.setup()

        if AgentRuntime._conn is None:
            AgentRuntime._conn = conn

        if AgentRuntime._llm is None:
            AgentRuntime._llm = MultiLLm([
                OpenRouterLLM("nvidia/nemotron-3-super-120b-a12b:free"),
                OpenRouterLLM("google/gemma-4-31b-it:free"),
                OpenRouterLLM("openrouter/free")
            ])

        if AgentRuntime._graph is None:
            AgentRuntime._graph = build_graph(
                llm = AgentRuntime._llm,
                conn=AgentRuntime._conn,
                table_name="jp_realestate_v1",
                checkpointer = AgentRuntime._checkpointer
            )

        if AgentRuntime._db is None:
            AgentRuntime._db = AgentMemory()

        self.agent_db = AgentRuntime._db
        self.llm = AgentRuntime._llm
        self.conn = AgentRuntime._conn
        self.agent = AgentRuntime._graph # it's the graph , just keep its name agent why not .
